import json
from pathlib import Path
from src.main import run_pipeline

ROOT = Path(__file__).resolve().parent.parent
SAMPLE = {
  "Product Name": "GlowBoost Vitamin C Serum",
  "Concentration": "10% Vitamin C",
  "Skin Type": "Oily, Combination",
  "Key Ingredients": "Vitamin C, Hyaluronic Acid",
  "Benefits": "Brightening, Fades dark spots",
  "How to Use": "Apply 2–3 drops in the morning before sunscreen",
  "Side Effects": "Mild tingling for sensitive skin",
  "Price": "₹699"
}

def test_pipeline_runs_and_outputs_json(tmp_path):
    outputs, meta = run_pipeline(SAMPLE, dry_run=True)
    assert "product_page" in outputs
    assert "faq" in outputs
    assert "comparison_page" in outputs
    # QA list length
    faq_list = outputs["faq"].get("faq", [])
    assert len(faq_list) >= 15
    # Product title
    assert outputs["product_page"]["title"].startswith("GlowBoost")
    # Meta consistent
    assert meta["run_id"]
    assert "timestamp" in meta
