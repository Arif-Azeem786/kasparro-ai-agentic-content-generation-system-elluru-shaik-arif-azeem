from .base_agent import BaseAgent
from typing import Dict

class ComparisonAgent(BaseAgent):
    def run(self, product) -> Dict:
        # Create a fictional Product B
        product_b = {
            "name": f"{product.name.split()[0]} Plus",
            "key_ingredients": [i + " Extract" for i in product.key_ingredients],
            "benefits": ["Brightening", "Hydration"],
            "price_inr": (product.price_inr or 700) + 100
        }
        # Simple comparison logic
        comparison = {
            "product_a": {"name": product.name, "price": product.price_inr, "ingredients": product.key_ingredients},
            "product_b": product_b,
            "differences": {
                "price_diff": (product_b["price_inr"] - (product.price_inr or 0))
            }
        }
        return comparison
