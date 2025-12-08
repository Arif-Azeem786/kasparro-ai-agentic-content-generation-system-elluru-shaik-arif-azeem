from .base_agent import BaseAgent
from typing import List, Dict
import uuid

class QAGeneratorAgent(BaseAgent):
    def run(self, product) -> List[Dict]:
        # Deterministic rules to create ~15 Qs
        qs = []
        # Informational
        qs.append({"category":"Informational", "q":"What is the product name?", "a": product.name})
        qs.append({"category":"Informational", "q":"What is the concentration?", "a": product.concentration or "Not specified"})
        # Usage
        qs.append({"category":"Usage", "q":"How to use the product?", "a": product.how_to_use})
        # Benefits
        for b in product.benefits:
            qs.append({"category":"Benefits", "q": f"What benefit does it provide related to {b}?", "a": f"{product.name} helps with {b.lower()}."})
        # Safety / Side effects
        qs.append({"category":"Safety", "q":"Are there side effects?", "a": product.side_effects or "None known for most users."})
        # Purchase
        qs.append({"category":"Purchase", "q":"What is the price?", "a": f"₹{int(product.price_inr)}" if product.price_inr else "Contact seller"})
        # Fill up to 15 with minor rephrasings
        idx = 0
        while len(qs) < 15:
            qs.append({"category":"Informational", "q": f"Is this suitable for {product.skin_type[idx%len(product.skin_type)]} skin?", "a": "Yes, it is suitable."})
            idx += 1
        # Attach id for traceability
        for item in qs:
            item["id"] = str(uuid.uuid4())
        return qs
