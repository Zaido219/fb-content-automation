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
        tone = brand_rules.get("brand_identity", {}).get(
            "tone", "Nostalgic, Warm"
        )

        style_directives = (
            f"Tone: {tone}. 90s retro anime screencap, hand-drawn anime background, "
            "cel-shaded animation style, vintage aesthetic, warm nostalgic color grading, "
            "soft analog film grain, VHS screen grab, retro television screenshot."
        )
        return f"{query}. {style_directives}"

    def orchestrate(self, query: str) -> ImageGenerationPayload:
        brand_rules = self._get_brand_rules()
        default_negatives = self._get_default_negatives()
        layout_specs = self._get_layout_specs()

        # 1. Build positive prompt with brand identity
        positive_prompt = self._transform_user_query(query, brand_rules)

        # 2. Combine default negatives + forbidden brand elements
        all_negatives = []
        for category in default_negatives.values():
            all_negatives.extend(category)

        # Extract forbidden_elements from brand_rules
        forbidden = (
            brand_rules.get("content_rules", {}).get("forbidden_elements", [])
        )
        all_negatives.extend(forbidden)

        negative_prompt_str = ", ".join(all_negatives)

        # 3. Extract layout spec
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
        "Goku eating fishballs at a street food cart in Manila"
    )
    print("PROMPT:", payload.prompt)
    print("\nNEGATIVE PROMPT:", payload.negative_prompt)