# src/tests/test_graph_pipeline.py
import os
from pathlib import Path
from src.graph.orchestrator import run_graph

def test_graph_runs_and_returns_state(tmp_path):
    raw_product = {
      "Product Name": "Test Serum",
      "Concentration": "10% Vitamin C",
      "Skin Type": "All",
      "Key Ingredients": "Vitamin C",
      "Benefits": "Brightening",
      "How to Use": "Apply",
      "Side Effects": "None",
      "Price": "100"
    }
    state = run_graph(raw_product, dry_run=True, use_hybrid_qa=False)
    assert isinstance(state, dict)
    # product and qa_pairs should exist
    assert "product" in state
    assert "qa_pairs" in state or state.get("qa_pairs") is not None
    # critique should always be present (even if "Needs revision" or "OK")
    assert "critique" in state
