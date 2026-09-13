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

    # method that combines all rules for the imagen api
    def orchestrate(self)->str:
        brand_rules = self._get_brand_rules()

        print(brand_rules)



if __name__ == "__main__":
    pb = PromptBuilder()
    pb.orchestrate()
        