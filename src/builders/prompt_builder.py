import os
import json

class PromptBuilder:
    def __init__(self): 
        self.base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))

    # helper method to read the brand rules file
    def _get_brand_rules(self):
        file_path = os.path.join(self.base_dir, "config", "brand_rules.json")

        with open(file_path, 'r') as file:
            return json.load(file)

    def _get_default_negatives(self):
        file_path = os.path.join(self.base_dir, "config", "default_negatives.json")

        with open(file_path, 'r') as file:
                return json.load(file)

    def _get_layout_specs(self):
        file_path = os.path.join(self.base_dir, "config", "layout_specs.json")

        with open(file_path, 'r') as file:
            return json.load(file)

    def _transform_user_query(self, query: str) -> str:
        """thin layer that will restructure user query to more structured LLM prompt"""
        style_directives = (
            "90s retro anime screencap, hand-drawn anime background, cel-shaded animation style, "
            "vintage aesthetic, warm nostalgic color grading, soft analog film grain, "
            "VHS screen grab, retro television screenshot."
        )
        return f"{query}. {style_directives}"

    # method that combines all rules for the imagen api
    def orchestrate(self, query: str) -> str:
        brand_rules = self._get_brand_rules()
        default_negatives = self._get_default_negatives()
        layout_specs = self._get_layout_specs()
        structured_prompt = self._transform_user_query(query)
        
        print(f"Final Structured Prompt: {structured_prompt}")
        return structured_prompt


if __name__ == "__main__":
    pb = PromptBuilder()
    # Testing with a sample Batang90 query
    pb.orchestrate("Goku eating fishballs at a street food cart in Manila")
        