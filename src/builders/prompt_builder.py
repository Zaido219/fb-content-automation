import json
import os
import re
from ..models.DTO import ImageGenerationPayload
from typing import Optional, List


class PromptBuilder:

    def __init__(self):
        self.base_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../")
        )

    def _load_config_json(self, file_name: str) -> dict:
        """Load and parse a JSON file from the config directory."""

        if not file_name:
            raise ValueError("No config file to load")

        file_path = os.path.join(self.base_dir, "config", file_name)

        try:
            with open(file_path, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            raise FileNotFoundError(f"config file not found: {file_path}") from None
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid json in config file: {file_path}") from e

    def _get_brand_rules(self) -> dict:
        return self._load_config_json("brand_rules.json")

    def _get_default_negatives(self) -> dict:
        return self._load_config_json("default_negatives.json")

    def _get_layout_specs(self) -> dict:
        return self._load_config_json("layout_specs.json")

    def _extract_pillar_terms(self, pillar: str) -> list[str]:
        """Extracts matchable keywords from a thematic pillar string, including
        parenthetical examples, e.g. 'Street food culture (taho, sorbetes)'
        -> ['Street food culture', 'taho', ' sorbetes']."""
        terms = [pillar.split("(")[0].strip()]
        match = re.search(r"\((.*?)\)", pillar)
        if match:
            terms.extend(match.group(1).split(","))
        return terms

    def _build_location_directives(self, query: str, thematic_pillars: list[str]) -> str:
        """Builds the setting/location directive string, preferring thematic pillars
        relevant to the query and falling back to the full pillar list if none match."""
        query_lower = query.lower()
        relevant = [
            pillar
            for pillar in thematic_pillars
            if any(term.strip().lower() in query_lower for term in self._extract_pillar_terms(pillar))
        ]
        pillars_to_use = relevant if relevant else thematic_pillars
        pillars_str = ", ".join(pillars_to_use) if pillars_to_use else "everyday Filipino neighborhood life"

        return (
            "Setting: Philippines, Manila street scene, authentic Filipino signage in "
            "Tagalog/Filipino text, tropical humid atmosphere. "
            f"Incorporate elements of: {pillars_str}. "
            "(not Chinese, not Japanese, not Thai, not Korean signage or architecture)."
        )

    def _inject_character_notes(self, query: str, character_list: dict) -> str:
        """Appends canonical design notes for any known character mentioned in the query,
        so approved designs stay consistent regardless of how the user phrases the request.
        Expects character_list as {character_name: design_notes}."""
        query_lower = query.lower()
        matched_notes = [
            f"{name}: {notes}"
            for name, notes in character_list.items()
            if name.split(" (")[0].strip().lower() in query_lower
        ]
        if not matched_notes:
            return ""
        return "Character design reference: " + "; ".join(matched_notes)

    def _transform_user_query(self, query: str, brand_rules: dict, thematic_pillars: list[str]) -> str:
        """Injects visual tone, brand identity, and relevant thematic setting into the positive prompt."""
        identity = brand_rules.get("brand_identity", {})
        tone = identity.get("tone", "Nostalgic, Warm")

        location_directives = self._build_location_directives(query, thematic_pillars)

        style_directives = (
            f"Tone: {tone}. "
            f"{location_directives} "
            "Photorealistic background and environment, real-world lighting, natural textures, "
            "shot on film, authentic location detail, realistic depth of field. "
            "The character is rendered in a completely different style from the background: "
            "cel-shaded 90s retro anime style, hand-drawn anime character, flat cel-shading, "
            "bold clean linework, vintage anime color palette. "
            "Style contrast: realistic photographic background, 2D animated character composited into it, "
            "like a cartoon character placed in a real photo. "
            "Overall grading: warm nostalgic color tone, soft analog film grain, VHS screen grab, "
            "retro television screenshot look applied evenly across the whole image."
        )
        return f"{query}. {style_directives}"

    def _resolve_negative_conflicts(self, positive_prompt: str, negatives: list[str]) -> list[str]:
        """Removes negative terms that directly contradict something requested in the positive prompt."""
        positive_lower = positive_prompt.lower()
        resolved = []
        for term in negatives:
            term_lower = term.strip().lower()
            if term_lower in positive_lower:
                continue
            resolved.append(term)
        return resolved

    def orchestrate(
        self,
        query: str,
        session_negative_prompts: Optional[List[str]] = None,
        few_shot_examples: Optional[List[str]] = None,
    ) -> ImageGenerationPayload:
        """Consolidates system prompts, brand guidelines, aspect ratios,
        session-level negative feedback, and few-shot memory into a single DTO
        payload.
        """
        # 1. Fetch configs
        brand_rules = self._get_brand_rules()
        default_negatives = self._get_default_negatives()
        layout_specs = self._get_layout_specs()

        content_rules = brand_rules.get("content_rules", {})
        thematic_pillars = content_rules.get("thematic_pillars", [])
        character_list = content_rules.get("character_list", {})

        # 2. Build base prompt with tone + relevant thematic setting
        positive_prompt = self._transform_user_query(query, brand_rules, thematic_pillars)

        # 3. Inject canonical character design notes, if any known character is referenced
        character_notes = self._inject_character_notes(query, character_list)
        if character_notes:
            positive_prompt = f"{positive_prompt}\n{character_notes}"

        # 4. Append few-shot memory context to positive prompt
        if few_shot_examples:
            recent_examples = few_shot_examples[-2:]  # Limit to 2 most recent
            examples_context = "\nStyle references from recent approved outputs:\n" + "\n".join(
                f"- {ex}" for ex in recent_examples
            )
            positive_prompt = f"{positive_prompt}\n{examples_context}"

        # 5. Aggregate all negative prompt sources
        all_negatives: List[str] = [
            item for sublist in default_negatives.values() for item in sublist
        ]

        forbidden_elements = content_rules.get("forbidden_elements", [])
        all_negatives.extend(forbidden_elements)

        # Ingest transient feedback from Streamlit rejections
        if session_negative_prompts:
            all_negatives.extend(session_negative_prompts)

        # 6. Resolve conflicts & deduplicate preserving insertion order
        resolved_negatives = self._resolve_negative_conflicts(
            positive_prompt, all_negatives
        )
        negative_prompt_str = ", ".join(dict.fromkeys(resolved_negatives))

        # 7. Extract layout aspect ratio safely
        default_layout_key = layout_specs.get("default_layout", "square")
        aspect_ratio = (
            layout_specs.get("layouts", {})
            .get(default_layout_key, {})
            .get("aspect_ratio", "1:1")
        )

        # 8. Build and return immutable DTO
        return ImageGenerationPayload(
            prompt=positive_prompt,
            negative_prompt=negative_prompt_str,
            aspect_ratio=aspect_ratio,
        )


if __name__ == "__main__":
    pb = PromptBuilder()
    payload = pb.orchestrate(
        "Sakuragi and friends, looking for clothes inside an ukay-ukay store"
    )
    print("PROMPT:", payload.prompt)
    print("\nNEGATIVE PROMPT:", payload.negative_prompt)