#!/usr/bin/env python3
"""
scripts/query_demo.py

Simple demo that:
- reads outputs/latest_run.json
- loads the corresponding faq_<run_id>.json
- prints 5 FAQ Q/A pairs
- if retrieval agent (simple or faiss) is available, runs a small example query
"""

from pathlib import Path
import json
import os
import sys

ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = ROOT / "outputs"

def load_latest():
    latest = OUTPUTS / "latest_run.json"
    if not latest.exists():
        print("No latest_run.json found in outputs/. Run pipeline first.")
        sys.exit(1)
    return json.loads(latest.read_text(encoding="utf-8"))

def load_faq(run_id):
    faq_path = OUTPUTS / f"faq_{run_id}.json"
    if not faq_path.exists():
        print(f"FAQ file not found: {faq_path}")
        sys.exit(1)
    return json.loads(faq_path.read_text(encoding="utf-8"))

def print_sample_faq(faq_json, n=5):
    faqs = faq_json.get("faq", [])[:n]
    print(f"\nShowing {len(faqs)} FAQ items (title: {faq_json.get('title')}):\n")
    for i, item in enumerate(faqs, 1):
        print(f"{i}. Q: {item.get('q')}")
        print(f"   A: {item.get('a')}\n")

def try_retrieval_demo(faq_json):
    import traceback
    # Try FAISS-backed retrieval first (if available)
    try:
        from src.agents.retrieval_agent import RetrievalAgent
        texts = [f"{it.get('q','')} {it.get('a','')}" for it in faq_json.get("faq", [])]
        agent = RetrievalAgent()
        agent.build_index(texts)
        q = "How to use the product?"
        top = agent.query(q, top_k=3)
        print("FAISS Retrieval demo (top matches):", top)
        return
    except Exception:
        print("FAISS retrieval failed or not available:")
        traceback.print_exc()

    # Fallback: try simple retrieval agent
    try:
        from src.agents.retrieval_agent_simple import RetrievalAgentSimple
        texts = [f"{it.get('q','')} {it.get('a','')}" for it in faq_json.get("faq", [])]
        agent = RetrievalAgentSimple()
        agent.build_index(texts)
        q = "How to use the product?"
        top = agent.query(q, top_k=3)
        print("Simple Retrieval demo (top matches):", top)
        return
    except Exception:
        print("Simple retrieval failed or not available:")
        traceback.print_exc()

    print("No retrieval agent available (FAISS or simple). Skipping retrieval demo.")

def main():
    latest = load_latest()
    run_id = latest.get("run_id")
    if not run_id:
        print("latest_run.json doesn't contain run_id")
        sys.exit(1)
    faq = load_faq(run_id)
    print_sample_faq(faq, n=5)
    try_retrieval_demo(faq)

if __name__ == "__main__":
    main()
