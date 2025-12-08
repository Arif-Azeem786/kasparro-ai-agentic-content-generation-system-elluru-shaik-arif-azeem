# src/tests/test_retrieval.py
import pytest
from src.agents.retrieval_agent import RetrievalAgent

SAMPLE_TEXTS = [
    "Apply 2-3 drops in the morning before sunscreen.",
    "Works well for oily and combination skin types.",
    "Contains Vitamin C and Hyaluronic Acid for brightening and hydration."
]

def test_retrieval_build_and_query():
    try:
        agent = RetrievalAgent()
    except RuntimeError:
        pytest.skip("FAISS / sentence-transformers not installed in this environment.")
    agent.build_index(SAMPLE_TEXTS)
    results = agent.query("How to use the product?", top_k=2)
    assert isinstance(results, list)
    assert len(results) <= 2
    # The expected best match contains "Apply 2-3 drops"
    assert any("Apply" in r or "apply" in r for r in results)
