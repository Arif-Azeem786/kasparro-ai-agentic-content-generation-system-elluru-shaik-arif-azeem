"""Orchestrator entrypoint for the agentic pipeline."""
import json
import uuid
from datetime import datetime,timezone
from pathlib import Path

# Import agents and models using the package-qualified path so relative imports inside
# agents (e.g., `from ..models.product_model import ProductModel`) work correctly.
from src.agents.parser_agent import ParserAgent
from src.agents.qa_agent import QAGeneratorAgent
from src.agents.content_block_agent import ContentBlockAgent
from src.agents.comparison_agent import ComparisonAgent
from src.agents.assembler_agent import AssemblerAgent


ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

# def current_meta():
#     return {
#         "run_id": str(uuid.uuid4()),
#         "timestamp": datetime.utcnow().isoformat() + "Z",
#     }
def current_meta():
    # use timezone-aware UTC timestamp
    return {
        "run_id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

def run_pipeline(raw_input, dry_run=False):
    meta = current_meta()
    # instantiate agents
    parser = ParserAgent()
    qa = QAGeneratorAgent()
    content = ContentBlockAgent()
    compare = ComparisonAgent()
    assembler = AssemblerAgent()

    product = parser.run(raw_input)
    qa_list = qa.run(product)
    blocks = content.run(product)
    comparison = compare.run(product)
    templates = {
        "product": {"title":"{{product.name}}", "sections":["benefits_block","ingredients_block","usage_block"], "include_faq": False},
        "faq": {"title":"FAQ - {{product.name}}", "sections":[], "include_faq": True},
        "comparison": {"title":"Comparison - {{product.name}} vs Fictional", "sections":["ingredients_block"], "include_faq": False}
    }
    outputs = assembler.run(product, blocks, qa_list, comparison, templates)

    # attach metadata
    for key, obj in [("product_page", outputs["product_page"]), ("faq", outputs["faq"]), ("comparison_page", outputs["comparison_page"])]:
        obj["_meta"] = {**meta, "source": key}

    # if not dry_run:
    #     with open(OUTPUT_DIR / f"product_page_{meta['run_id']}.json","w") as f:
    #         json.dump(outputs["product_page"], f, indent=2, ensure_ascii=False)
    #     with open(OUTPUT_DIR / f"faq_{meta['run_id']}.json","w") as f:
    #         json.dump(outputs["faq"], f, indent=2, ensure_ascii=False)
    #     with open(OUTPUT_DIR / f"comparison_page_{meta['run_id']}.json","w") as f:
    #         json.dump(outputs["comparison_page"], f, indent=2, ensure_ascii=False)
    if not dry_run:
        # write with explicit utf-8 encoding to avoid Windows encoding errors
        with open(OUTPUT_DIR / f"product_page_{meta['run_id']}.json", "w", encoding="utf-8") as f:
            json.dump(outputs["product_page"], f, indent=2, ensure_ascii=False)
        with open(OUTPUT_DIR / f"faq_{meta['run_id']}.json", "w", encoding="utf-8") as f:
            json.dump(outputs["faq"], f, indent=2, ensure_ascii=False)
        with open(OUTPUT_DIR / f"comparison_page_{meta['run_id']}.json", "w", encoding="utf-8") as f:
            json.dump(outputs["comparison_page"], f, indent=2, ensure_ascii=False)

    # also save a "latest" pointer (utf-8 as well)
    with open(OUTPUT_DIR / "latest_run.json", "w", encoding="utf-8") as f:
        json.dump({"run_id": meta["run_id"], "timestamp": meta["timestamp"]}, f, ensure_ascii=False)

    # also save a "latest" pointer
    with open(OUTPUT_DIR / "latest_run.json","w") as f:
        json.dump({"run_id": meta["run_id"], "timestamp": meta["timestamp"]}, f)

    return outputs, meta

if __name__ == "__main__":
    raw_product = {
      "Product Name": "GlowBoost Vitamin C Serum",
      "Concentration": "10% Vitamin C",
      "Skin Type": "Oily, Combination",
      "Key Ingredients": "Vitamin C, Hyaluronic Acid",
      "Benefits": "Brightening, Fades dark spots",
      "How to Use": "Apply 2–3 drops in the morning before sunscreen",
      "Side Effects": "Mild tingling for sensitive skin",
      "Price": "₹699"
    }
    outputs, meta = run_pipeline(raw_product)
    print("Run complete:", meta)
