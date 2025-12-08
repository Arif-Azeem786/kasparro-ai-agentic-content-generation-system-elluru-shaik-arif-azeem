# src/tests/test_llm_interface.py
import os
from src.agents.llm_qa_agent import HybridQAGeneratorAgent
from src.models.product_model import ProductModel

def test_hybrid_agent_fallback():
    # ensure agent runs deterministically when OPENAI_API_KEY not set
    if os.getenv("OPENAI_API_KEY"):
        pytest.skip("This test checks deterministic fallback when no API key is set.")
    agent = HybridQAGeneratorAgent()
    product = ProductModel(
        name="GlowBoost Vitamin C Serum",
        concentration="10% Vitamin C",
        skin_type=["Oily", "Combination"],
        key_ingredients=["Vitamin C","Hyaluronic Acid"],
        benefits=["Brightening","Fades dark spots"],
        how_to_use="Apply 2–3 drops in the morning before sunscreen",
        side_effects="Mild tingling for sensitive skin",
        price_inr=699.0
    )
    qa = agent.run(product)
    assert isinstance(qa, list)
    assert len(qa) >= 15
