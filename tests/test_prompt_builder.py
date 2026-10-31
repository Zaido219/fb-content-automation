import tempfile
import unittest
from pathlib import Path

from src.builders.prompt_builder import PromptBuilder


class PromptBuilderTests(unittest.TestCase):
    def setUp(self) -> None:
        self.builder = PromptBuilder()

    def test_build_prompt_uses_configured_style_and_layout(self) -> None:
        payload = self.builder.build_prompt("Goku eating taho")

        self.assertIn("cel-shaded 90s retro anime style", payload.prompt)
        self.assertIn("Street food culture", payload.prompt)
        self.assertIn("Goku (Dragon Ball): spiky black hair", payload.prompt)
        self.assertEqual(payload.aspect_ratio, "4:3")

    def test_pillar_matching_is_case_insensitive_and_word_bounded(self) -> None:
        pillars = [
            "Street food culture (taho, sorbetes)",
            "Public transport (Jeepney, Tricycle)",
        ]

        selected = self.builder._build_location_directives("Buy TAHO!", pillars)
        fallback = self.builder._build_location_directives("Buy tahoe!", pillars)

        self.assertIn("Street food culture", selected)
        self.assertNotIn("Public transport", selected)
        self.assertIn("Public transport", fallback)

    def test_character_matching_does_not_match_inside_other_words(self) -> None:
        characters = {"Goku (Dragon Ball)": "spiky black hair"}

        self.assertEqual(self.builder._inject_character_notes("Gokul", characters), "")
        self.assertIn("spiky black hair", self.builder._inject_character_notes("Goku!", characters))

    def test_negative_prompt_filters_conflicts_and_deduplicates_case_insensitively(self) -> None:
        result = self.builder._build_negative_prompt(
            "A smartphone is on the table.",
            {"quality": ["blurry", "blurry", "smartphone"]},
            {"forbidden_elements": []},
            ["EXTRA", "extra"],
        )

        self.assertEqual(result, "blurry, EXTRA")

    def test_few_shot_context_uses_only_two_most_recent_examples(self) -> None:
        prompt = self.builder.build_prompt(
            "A neighborhood scene",
            few_shot_examples=["old", "middle", "recent"],
        ).prompt

        self.assertNotIn("- old", prompt)
        self.assertIn("- middle", prompt)
        self.assertIn("- recent", prompt)

    def test_brand_rules_require_style_directives(self) -> None:
        with self.assertRaisesRegex(ValueError, "style_directives"):
            self.builder._validate_config("brand_rules.json", {})

    def test_default_negatives_require_string_lists(self) -> None:
        with self.assertRaisesRegex(ValueError, "string lists"):
            self.builder._validate_config(
                "default_negatives.json", {"quality": ["blurry", 3]}
            )

    def test_layout_default_must_reference_a_valid_layout(self) -> None:
        with self.assertRaisesRegex(ValueError, "not defined in layouts"):
            self.builder._validate_config(
                "layout_specs.json",
                {"default_layout": "missing", "layouts": {"square": {"aspect_ratio": "1:1"}}},
            )

    def test_config_root_must_be_a_json_object(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            config_dir = Path(directory) / "config"
            config_dir.mkdir()
            (config_dir / "default_negatives.json").write_text("[]", encoding="utf-8")
            self.builder.base_dir = Path(directory)

            with self.assertRaisesRegex(ValueError, "expected a JSON object"):
                self.builder._get_default_negatives()


if __name__ == "__main__":
    unittest.main()
