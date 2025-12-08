from .base_agent import BaseAgent
from ..models.product_model import ProductModel

class ParserAgent(BaseAgent):
    def run(self, raw: dict) -> ProductModel:
        # minimal normalization logic
        cleaned = {
            "name": raw.get("Product Name") or raw.get("name"),
            "concentration": raw.get("Concentration"),
            "skin_type": [s.strip() for s in (raw.get("Skin Type") or "").split(",") if s.strip()],
            "key_ingredients": [i.strip() for i in (raw.get("Key Ingredients") or "").split(",") if i.strip()],
            "benefits": [b.strip() for b in (raw.get("Benefits") or "").split(",") if b.strip()],
            "how_to_use": raw.get("How to Use") or "",
            "side_effects": raw.get("Side Effects"),
            "price_inr": float(raw.get("Price").replace("₹","").strip()) if raw.get("Price") else None
        }
        return ProductModel(**cleaned)
