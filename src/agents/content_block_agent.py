from .base_agent import BaseAgent
from typing import Dict

class ContentBlockAgent(BaseAgent):
    def run(self, product) -> Dict:
        blocks = {}
        # Benefits block (rule-based)
        blocks["benefits_block"] = {
            "summary": ", ".join(product.benefits),
            "bullets": [f"{b} — ideal for {', '.join(product.skin_type)} skin." for b in product.benefits]
        }
        # Ingredients block
        blocks["ingredients_block"] = {
            "list": product.key_ingredients,
            "note": f"Concentration: {product.concentration}" if product.concentration else ""
        }
        # Usage block
        blocks["usage_block"] = {"how": product.how_to_use}
        # Safety
        blocks["safety_block"] = {"side_effects": product.side_effects or "Mild or none."}
        return blocks
