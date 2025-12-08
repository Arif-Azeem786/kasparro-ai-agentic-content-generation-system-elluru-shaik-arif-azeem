"""
Orchestrator entrypoint for the agentic pipeline.

Features:
- Instantiates Parser / QA / Content / Comparison / Assembler agents.
- Optional Hybrid QA agent if OPENAI_API_KEY is set.
- Optional RetrievalAgent if ENABLE_RETRIEVAL=1 (graceful fallback when faiss not installed).
- Writes outputs as UTF-8 JSON with metadata (run_id, timestamp, source).
- CLI flags: --dry-run (don't write outputs), --debug (print extra logs).
"""

import os
import sys
import json
import uuid
import argparse
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Tuple, Dict, Any

# Base deterministic agents (always available)
from src.agents.parser_agent import ParserAgent
from src.agents.qa_agent import QAGeneratorAgent
from src.agents.content_block_agent import ContentBlockAgent
from src.agents.comparison_agent import ComparisonAgent
from src.agents.assembler_agent import AssemblerAgent

# Optional agents will be imported conditionally
RetrievalAgent = None
HybridQAClass = None

# Project layout
ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

# Logging setup (will be configured in main)
logger = logging.getLogger("orchestrator")


def current_meta() -> Dict[str, str]:
    """Return run metadata with timezone-aware UTC timestamp."""
    return {
        "run_id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def import_optional_agents(enable_retrieval: bool, use_hybrid_qa: bool) -> Tuple[Optional[Any], Optional[Any]]:
    """
    Try importing optional agents. Returns (RetrievalAgentClass or None, HybridQAClass or None).
    Prefer faiss-based RetrievalAgent, but fall back to retrieval_agent_simple if faiss not available.
    """
    retrieval_cls = None
    hybrid_cls = None

    if enable_retrieval:
        # Try faiss-backed agent first
        try:
            from src.agents.retrieval_agent import RetrievalAgent as RA
            retrieval_cls = RA
            logger.info("Using FAISS-backed RetrievalAgent.")
        except Exception as e_faiss:
            logger.warning("FAISS RetrievalAgent import failed: %s. Trying simple retrieval fallback.", e_faiss)
            # Try the simple numpy fallback
            try:
                from src.agents.retrieval_agent_simple import RetrievalAgentSimple as RAS
                retrieval_cls = RAS
                logger.info("Using simple RetrievalAgent fallback (no FAISS).")
            except Exception as e_simple:
                logger.warning("Simple RetrievalAgent fallback also failed: %s", e_simple)
                retrieval_cls = None

    if use_hybrid_qa:
        try:
            from src.agents.llm_qa_agent import HybridQAGeneratorAgent as HQA
            hybrid_cls = HQA
            logger.info("HybridQAGeneratorAgent imported successfully.")
        except Exception as e:
            logger.warning("Hybrid QA agent not available: %s", e)

    return retrieval_cls, hybrid_cls


def write_json(path: Path, data: Dict, *, ensure_ascii: bool = False) -> None:
    """Write JSON to file with utf-8 encoding safely."""
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=ensure_ascii)
    tmp.replace(path)


def run_pipeline(raw_input: Dict[str, Any], dry_run: bool = False, enable_retrieval: bool = False, use_hybrid_qa: bool = False) -> Tuple[Dict[str, Any], Dict[str, str]]:
    """
    Execute pipeline and return (outputs, meta).
    outputs is a dict with keys: product_page, faq, comparison_page (each a dict).
    """
    meta = current_meta()
    logger.info("Starting pipeline run %s", meta["run_id"])

    # Optional imports
    retrieval_cls, hybrid_cls = import_optional_agents(enable_retrieval, use_hybrid_qa)

    # Choose QA agent class
    if hybrid_cls:
        QAClass = hybrid_cls
        logger.info("Using HybridQA agent (LLM-enabled).")
    else:
        QAClass = QAGeneratorAgent
        logger.info("Using deterministic QAGeneratorAgent.")

    # Instantiate agents
    parser = ParserAgent()
    qa_agent = QAClass()
    content_agent = ContentBlockAgent()
    comparison_agent = ComparisonAgent()
    assembler = AssemblerAgent()

    # Run agents in sequence
    product = parser.run(raw_input)
    logger.debug("Parsed product model: %s", getattr(product, "dict", lambda: str(product))())

    qa_list = qa_agent.run(product)
    logger.debug("Generated %d QA items.", len(qa_list))

    blocks = content_agent.run(product)
    logger.debug("Generated content blocks: %s", list(blocks.keys()))

    comparison = comparison_agent.run(product)
    logger.debug("Generated comparison block.")

    # Optional: build retrieval index over QA corpus or blocks
    retrieval_agent = None
    if retrieval_cls:
        try:
            retrieval_agent = retrieval_cls()
            # Build corpus from QA (question + answer) and from blocks if desired
            corpus = [f"{item.get('q','')} {item.get('a','')}" for item in qa_list]
            # also append block summaries if available
            for k, v in blocks.items():
                if isinstance(v, dict):
                    # join textual pieces of block
                    block_text = " ".join([str(x) for x in v.values()])
                    corpus.append(block_text)
            retrieval_agent.build_index(corpus)
            logger.info("Retrieval index built with %d documents.", len(corpus))
        except Exception as e:
            logger.warning("Failed to build retrieval index: %s", e)
            retrieval_agent = None

    # Templates (kept simple; these live in src/templates in your repo if you prefer)
    templates = {
        "product": {"title": "{{product.name}}", "sections": ["benefits_block", "ingredients_block", "usage_block"], "include_faq": False},
        "faq": {"title": "FAQ - {{product.name}}", "sections": [], "include_faq": True},
        "comparison": {"title": "Comparison - {{product.name}} vs Fictional", "sections": ["ingredients_block"], "include_faq": False}
    }

    outputs = assembler.run(product, blocks, qa_list, comparison, templates)

    # Attach metadata to each output
    for key, obj in (("product_page", outputs["product_page"]), ("faq", outputs["faq"]), ("comparison_page", outputs["comparison_page"])):
        if isinstance(obj, dict):
            obj["_meta"] = {**meta, "source": key}

    # Persist outputs unless dry_run
    if not dry_run:
        product_path = OUTPUT_DIR / f"product_page_{meta['run_id']}.json"
        faq_path = OUTPUT_DIR / f"faq_{meta['run_id']}.json"
        comp_path = OUTPUT_DIR / f"comparison_page_{meta['run_id']}.json"

        write_json(product_path, outputs["product_page"], ensure_ascii=False)
        write_json(faq_path, outputs["faq"], ensure_ascii=False)
        write_json(comp_path, outputs["comparison_page"], ensure_ascii=False)

        # latest pointer
        latest = {"run_id": meta["run_id"], "timestamp": meta["timestamp"]}
        write_json(OUTPUT_DIR / "latest_run.json", latest, ensure_ascii=False)
        logger.info("Wrote outputs to %s (run_id=%s)", OUTPUT_DIR, meta["run_id"])

    logger.info("Pipeline run complete: %s", meta)
    return outputs, meta


def parse_args(argv=None):
    p = argparse.ArgumentParser(prog="agentic-pipeline", description="Run agentic content generation pipeline.")
    p.add_argument("--dry-run", action="store_true", help="Run pipeline without writing outputs.")
    p.add_argument("--enable-retrieval", action="store_true", help="Enable RetrievalAgent (FAISS).")
    p.add_argument("--debug", action="store_true", help="Enable debug logging.")
    return p.parse_args(argv)


def configure_logging(debug: bool = False):
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)-7s %(name)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    # reduce noise from external libs (if desired)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


def main():
    args = parse_args()
    configure_logging(args.debug)
    # detect OpenAI usage by env var
    use_hybrid_qa = bool(os.getenv("OPENAI_API_KEY"))
    enable_retrieval = args.enable_retrieval or bool(os.getenv("ENABLE_RETRIEVAL"))
    if args.debug:
        logger.debug("env.OPENAI_API_KEY present: %s", bool(os.getenv("OPENAI_API_KEY")))
        logger.debug("enable_retrieval flag: %s", enable_retrieval)

    # Simple raw product input (assignment-provided data)
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

    try:
        outputs, meta = run_pipeline(raw_product, dry_run=args.dry_run, enable_retrieval=enable_retrieval, use_hybrid_qa=use_hybrid_qa)
        print("Run complete:", meta)
    except Exception as e:
        logger.exception("Pipeline failed with an exception: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
