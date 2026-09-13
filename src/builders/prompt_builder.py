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

    # method that combines all rules for the imagen api
    def orchestrate(self)->str:
        brand_rules = self._get_brand_rules()
        defualt_negatives = self._get_default_negatives()
        layout_specs = self._get_layout_specs()

        print(layout_specs)



if __name__ == "__main__":
    pb = PromptBuilder()
    pb.orchestrate()
        