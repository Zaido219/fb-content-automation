import json
import os
from ..models.DTO import ImageGenerationPayload


class PromptBuilder:

    def __init__(self):
        self.base_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../")
        )

    def _get_brand_rules(self) -> dict:
        file_path = os.path.join(self.base_dir, "config", "brand_rules.json")
        with open(file_path, "r") as file:
            return json.load(file)

    def _get_default_negatives(self) -> dict:
        file_path = os.path.join(
            self.base_dir, "config", "default_negatives.json"
        )
        with open(file_path, "r") as file:
            return json.load(file)

    def _get_layout_specs(self) -> dict:
        file_path = os.path.join(self.base_dir, "config", "layout_specs.json")
        with open(file_path, "r") as file:
            return json.load(file)

    def _transform_user_query(self, query: str, brand_rules: dict) -> str:
        """Injects visual tone and core brand identity into the positive prompt."""
        identity = brand_rules.get("brand_identity", {})
        tone = identity.get("tone", "Nostalgic, Warm")
        language = identity.get("primary_language", "Taglish")

        location_directives = (
            "Setting: Philippines, Manila street scene, authentic Filipino signage in Tagalog/Filipino text, "
            "sari-sari store style storefronts, tropical humid atmosphere, Filipino street food cart aesthetic "
            "(not Chinese, not Japanese, not Thai, not Korean signage or architecture)."
        )

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

    def orchestrate(self, query: str) -> ImageGenerationPayload:
        brand_rules = self._get_brand_rules()
        default_negatives = self._get_default_negatives()
        layout_specs = self._get_layout_specs()

        positive_prompt = self._transform_user_query(query, brand_rules)

        all_negatives = []
        for category in default_negatives.values():
            all_negatives.extend(category)

        forbidden = brand_rules.get("content_rules", {}).get("forbidden_elements", [])
        all_negatives.extend(forbidden)

        # Strip negatives that contradict what the positive prompt explicitly asks for
        all_negatives = self._resolve_negative_conflicts(positive_prompt, all_negatives)
        negative_prompt_str = ", ".join(dict.fromkeys(all_negatives))  # dedupe too

        default_layout_key = layout_specs.get("default_layout", "square")
        aspect_ratio = (
            layout_specs.get("layouts", {})
            .get(default_layout_key, {})
            .get("aspect_ratio", "1:1")
        )

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