from pydantic import BaseModel
from typing import List, Optional

class ProductModel(BaseModel):
    name: str
    concentration: Optional[str]
    skin_type: List[str]
    key_ingredients: List[str]
    benefits: List[str]
    how_to_use: str
    side_effects: Optional[str]
    price_inr: Optional[float]
