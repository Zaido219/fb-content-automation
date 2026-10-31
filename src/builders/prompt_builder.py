import json
import re
from pathlib import Path
from typing import Any

from ..models.DTO import ImageGenerationPayload


class PromptBuilder:
    def __init__(self) -> None:
        self.base_dir = Path(__file__).resolve().parents[2]

    def _load_config_json(self, file_name: str) -> dict[str, Any]:
        """Load, parse, and validate a JSON config file."""
        if not file_name:
            raise ValueError("No config file to load")

        file_path = self.base_dir / "config" / file_name
        try:
            with file_path.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except FileNotFoundError:
            raise FileNotFoundError(f"config file not found: {file_path}") from None
        except json.JSONDecodeError as error:
            raise ValueError(f"Invalid json in config file: {file_path}") from error

        if not isinstance(data, dict):
            raise ValueError(f"Invalid config in {file_path}: expected a JSON object")

        self._validate_config(file_name, data, file_path)
        return data

    def _validate_config(
        self, file_name: str, data: dict[str, Any], file_path: Path | None = None
    ) -> None:
        """Validate fields consumed by prompt generation."""
        location = str(file_path or file_name)

        if file_name == "brand_rules.json":
            identity = data.get("brand_identity", {})
            if not isinstance(identity, dict):
                raise ValueError(f"Invalid config in {location}: brand_identity must be an object")
            if "tone" in identity and not isinstance(identity["tone"], str):
                raise ValueError(f"Invalid config in {location}: brand_identity.tone must be a string")

            style_directives = data.get("style_directives")
            if not isinstance(style_directives, str) or not style_directives.strip():
                raise ValueError(f"Invalid config in {location}: style_directives must be a non-empty string")

            content_rules = data.get("content_rules", {})
            if not isinstance(content_rules, dict):
                raise ValueError(f"Invalid config in {location}: content_rules must be an object")

            self._validate_string_list(
                content_rules.get("thematic_pillars", []),
                "content_rules.thematic_pillars",
                location,
            )
            self._validate_string_list(
                content_rules.get("forbidden_elements", []),
                "content_rules.forbidden_elements",
                location,
            )
            character_list = content_rules.get("character_list", {})
            if not isinstance(character_list, dict) or not all(
                isinstance(name, str) and isinstance(notes, str)
                for name, notes in character_list.items()
            ):
                raise ValueError(
                    f"Invalid config in {location}: content_rules.character_list "
                    "must map strings to strings"
                )

        elif file_name == "default_negatives.json":
            if not all(
                isinstance(category, str)
                and isinstance(terms, list)
                and all(isinstance(term, str) for term in terms)
                for category, terms in data.items()
            ):
                raise ValueError(
                    f"Invalid config in {location}: expected an object of string lists"
                )

        elif file_name == "layout_specs.json":
            default_layout = data.get("default_layout")
            layouts = data.get("layouts")
            if not isinstance(default_layout, str) or not default_layout:
                raise ValueError(
                    f"Invalid config in {location}: default_layout must be a non-empty string"
                )
            if not isinstance(layouts, dict) or not layouts:
                raise ValueError(f"Invalid config in {location}: layouts must be a non-empty object")
            if default_layout not in layouts:
                raise ValueError(
                    f"Invalid config in {location}: default_layout "
                    f"{default_layout!r} is not defined in layouts"
                )
            for name, layout in layouts.items():
                if (
                    not isinstance(name, str)
                    or not isinstance(layout, dict)
                    or not isinstance(layout.get("aspect_ratio"), str)
                    or not layout["aspect_ratio"].strip()
                ):
                    raise ValueError(
                        f"Invalid config in {location}: each layout must have a "
                        "non-empty string aspect_ratio"
                    )

    @staticmethod
    def _validate_string_list(value: Any, field: str, location: str) -> None:
        if not isinstance(value, list) or not all(
            isinstance(item, str) for item in value
        ):
            raise ValueError(f"Invalid config in {location}: {field} must be a list of strings")

    def _get_brand_rules(self) -> dict[str, Any]:
        return self._load_config_json("brand_rules.json")

    def _get_default_negatives(self) -> dict[str, Any]:
        return self._load_config_json("default_negatives.json")

    def _get_layout_specs(self) -> dict[str, Any]:
        return self._load_config_json("layout_specs.json")

    @staticmethod
    def _contains_phrase(text: str, phrase: str) -> bool:
        """Match a phrase case-insensitively without matching inside other words."""
        words = phrase.split()
        if not words:
            return False
        pattern = r"(?<!\w)" + r"\s+".join(re.escape(word) for word in words) + r"(?!\w)"
        return re.search(pattern, text, flags=re.IGNORECASE) is not None

    def _extract_pillar_terms(self, pillar: str) -> list[str]:
        """Extract matchable keywords, including parenthetical examples."""
        terms = [pillar.split("(", 1)[0].strip()]
        match = re.search(r"\((.*?)\)", pillar)
        if match:
            terms.extend(term.strip() for term in match.group(1).split(","))
        return [term for term in terms if term]

    def _build_location_directives(
        self, query: str, thematic_pillars: list[str]
    ) -> str:
        """Choose query-relevant thematic pillars, or use all pillars as a fallback."""
        relevant = [
            pillar
            for pillar in thematic_pillars
            if any(
                self._contains_phrase(query, term)
                for term in self._extract_pillar_terms(pillar)
            )
        ]
        pillars_to_use = relevant if relevant else thematic_pillars
        pillars_str = (
            ", ".join(pillars_to_use)
            if pillars_to_use
            else "everyday Filipino neighborhood life"
        )

        return (
            "Setting: Philippines, Manila street scene, authentic Filipino signage in "
            "Tagalog/Filipino text, tropical humid atmosphere. "
            f"Incorporate elements of: {pillars_str}. "
            "(not Chinese, not Japanese, not Thai, not Korean signage or architecture)."
        )

    def _inject_character_notes(
        self, query: str, character_list: dict[str, str]
    ) -> str:
        """Append design notes for known characters mentioned in the query."""
        matched_notes = [
            f"{name}: {notes}"
            for name, notes in character_list.items()
            if self._contains_phrase(query, name.split(" (", 1)[0].strip())
        ]
        if not matched_notes:
            return ""
        return "Character design reference: " + "; ".join(matched_notes)

    def _transform_user_query(
        self,
        query: str,
        brand_rules: dict[str, Any],
        thematic_pillars: list[str],
    ) -> str:
        """Inject tone, brand identity, and relevant setting into the user prompt."""
        identity = brand_rules.get("brand_identity", {})
        tone = identity.get("tone", "Nostalgic, Warm")
        style_directives = brand_rules["style_directives"]
        location_directives = self._build_location_directives(query, thematic_pillars)
        return f"{query}. Tone: {tone}. {location_directives} {style_directives}"

    def _resolve_negative_conflicts(
        self, positive_prompt: str, negatives: list[str]
    ) -> list[str]:
        """Remove negative phrases that are explicitly present in the positive prompt."""
        return [
            term
            for term in negatives
            if term.strip() and not self._contains_phrase(positive_prompt, term.strip())
        ]

    def _build_positive_prompt(
        self,
        query: str,
        brand_rules: dict[str, Any],
        content_rules: dict[str, Any],
        few_shot_examples: list[str] | None,
    ) -> str:
        positive_prompt = self._transform_user_query(
            query,
            brand_rules,
            content_rules.get("thematic_pillars", []),
        )

        character_notes = self._inject_character_notes(
            query, content_rules.get("character_list", {})
        )
        if character_notes:
            positive_prompt = f"{positive_prompt}\n{character_notes}"

        if few_shot_examples:
            examples_context = "\nStyle references from recent approved outputs:\n" + "\n".join(
                f"- {example}" for example in few_shot_examples[-2:]
            )
            positive_prompt = f"{positive_prompt}{examples_context}"

        return positive_prompt

    def _build_negative_prompt(
        self,
        positive_prompt: str,
        default_negatives: dict[str, list[str]],
        content_rules: dict[str, Any],
        session_negative_prompts: list[str] | None,
    ) -> str:
        all_negatives = [
            term for terms in default_negatives.values() for term in terms
        ]
        all_negatives.extend(content_rules.get("forbidden_elements", []))
        if session_negative_prompts:
            all_negatives.extend(session_negative_prompts)

        resolved = self._resolve_negative_conflicts(positive_prompt, all_negatives)
        unique_terms: dict[str, str] = {}
        for term in resolved:
            unique_terms.setdefault(term.casefold(), term)
        return ", ".join(unique_terms.values())

    @staticmethod
    def _get_aspect_ratio(layout_specs: dict[str, Any]) -> str:
        default_layout = layout_specs["default_layout"]
        return layout_specs["layouts"][default_layout]["aspect_ratio"]

    def build_prompt(
        self,
        query: str,
        session_negative_prompts: list[str] | None = None,
        few_shot_examples: list[str] | None = None,
    ) -> ImageGenerationPayload:
        """Build the complete image-generation payload from config and session context."""
        brand_rules = self._get_brand_rules()
        default_negatives = self._get_default_negatives()
        layout_specs = self._get_layout_specs()
        content_rules = brand_rules.get("content_rules", {})

        positive_prompt = self._build_positive_prompt(
            query, brand_rules, content_rules, few_shot_examples
        )
        negative_prompt = self._build_negative_prompt(
            positive_prompt,
            default_negatives,
            content_rules,
            session_negative_prompts,
        )

        return ImageGenerationPayload(
            prompt=positive_prompt,
            negative_prompt=negative_prompt,
            aspect_ratio=self._get_aspect_ratio(layout_specs),
        )


if __name__ == "__main__":
    pb = PromptBuilder()
    payload = pb.build_prompt(
        "Sakuragi and friends, looking for clothes inside an ukay-ukay store"
    )
    print("PROMPT:", payload.prompt)
    print("\nNEGATIVE PROMPT:", payload.negative_prompt)
