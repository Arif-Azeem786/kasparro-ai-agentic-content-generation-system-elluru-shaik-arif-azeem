# src/main.py
import os
import sys
import argparse
import logging
from pathlib import Path
from src.graph.orchestrator import run_graph

ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

logger = logging.getLogger("agentic-graph")


def parse_args(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--debug", action="store_true")
    p.add_argument("--enable-llm", action="store_true", help="enable hybrid LLM QA (requires OPENAI_API_KEY)")
    return p.parse_args(argv)


def configure_logging(debug=False):
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s %(levelname)s - %(message)s")


def write_json(path: Path, data, *, ensure_ascii=False):
    import json
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=ensure_ascii)
    tmp.replace(path)


def main():
    args = parse_args()
    configure_logging(args.debug)

    use_hybrid = args.enable_llm and bool(os.getenv("OPENAI_API_KEY"))

    # sample input (assignment example)
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

    final_state = run_graph(raw_product, dry_run=args.dry_run, use_hybrid_qa=use_hybrid)

    # -----------------------------
    # NEW: SAFE PRODUCT NAME EXTRACTION
    # -----------------------------
    product = final_state.get("product")

    # If it's a Pydantic model → convert to dict
    if hasattr(product, "model_dump"):
        product_dict = product.model_dump()
    elif isinstance(product, dict):
        product_dict = product
    else:
        product_dict = {}

    product_name = (
        product_dict.get("name")
        or product_dict.get("Product Name")
        or "Unknown Product"
    )

    # Construct FAQ output safely
    faq = {
        "title": f"FAQ - {product_name}",
        "faq": final_state.get("qa_pairs", [])
    }

    # Write outputs if not dry-run
    if not args.dry_run:
        import time
        ts = final_state.get("run_id") or str(time.time())

        draft = final_state.get("draft_page")
        if draft:
            write_json(OUTPUT_DIR / f"product_page_{ts}.json", draft, ensure_ascii=False)

        write_json(OUTPUT_DIR / f"faq_{ts}.json", faq, ensure_ascii=False)

    print("Graph run complete. approved:", final_state.get("approved"))
    print("Critique:", final_state.get("critique"))


if __name__ == "__main__":
    main()
