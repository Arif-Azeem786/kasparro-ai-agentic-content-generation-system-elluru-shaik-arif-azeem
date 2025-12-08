#!/usr/bin/env python3
"""
Interactive QA tester.

Usage:
  python scripts/interactive_qa.py

Type a question at the prompt and press Enter.
Type "exit" or "quit" to leave.
"""
import json
from pathlib import Path
import os
import sys

ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = ROOT / "outputs"

def load_latest_faq():
    latest = OUTPUTS / "latest_run.json"
    if not latest.exists():
        print("No latest_run.json found — run pipeline first (python -m src.main).")
        sys.exit(1)
    lr = json.loads(latest.read_text(encoding="utf-8"))
    run_id = lr.get("run_id")
    if not run_id:
        print("latest_run.json missing run_id")
        sys.exit(1)
    faq_path = OUTPUTS / f"faq_{run_id}.json"
    if not faq_path.exists():
        print(f"faq file not found: {faq_path}")
        sys.exit(1)
    return json.loads(faq_path.read_text(encoding="utf-8"))

def try_retrieval_agent(faq_json, query):
    # try FAISS
    try:
        from src.agents.retrieval_agent import RetrievalAgent
        agent = RetrievalAgent()
        corpus = [f"{it.get('q','')} {it.get('a','')}" for it in faq_json.get("faq",[])]
        agent.build_index(corpus)
        matches = agent.query(query, top_k=1)
        if matches:
            return matches[0]
    except Exception:
        pass

    # try simple retrieval
    try:
        from src.agents.retrieval_agent_simple import RetrievalAgentSimple
        agent = RetrievalAgentSimple()
        corpus = [f"{it.get('q','')} {it.get('a','')}" for it in faq_json.get("faq",[])]
        agent.build_index(corpus)
        matches = agent.query(query, top_k=1)
        if matches:
            return matches[0]
    except Exception:
        pass

    return None

def substring_fallback(faq_json, query):
    q = query.lower()
    for it in faq_json.get("faq", []):
        if it.get("q","").lower() == q:
            return it.get("a")
    # partial substring match
    for it in faq_json.get("faq", []):
        if q in it.get("q","").lower() or q in it.get("a","").lower():
            return it.get("a")
    return None

def maybe_refine_with_llm(query, answer, product):
    # optional: refine using HybridQAGeneratorAgent if OPENAI_API_KEY is set
    if not os.getenv("OPENAI_API_KEY"):
        return answer
    try:
        from src.agents.llm_qa_agent import HybridQAGeneratorAgent
        agent = HybridQAGeneratorAgent()
        # create a tiny product-like object for context if needed
        refined_list = agent._maybe_refine_with_openai(query, answer, product) if hasattr(agent, "_maybe_refine_with_openai") else None
        return refined_list or answer
    except Exception:
        return answer

def interactive_loop():
    faq_json = load_latest_faq()
    product = {}  # not required, but passed to LLM refine if present
    print(f"Loaded FAQ: {faq_json.get('title')}. Ask a question (type 'exit' to quit).")
    while True:
        try:
            query = input("\n> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nbye")
            break
        if not query:
            continue
        if query.lower() in ("exit","quit"):
            print("bye")
            break

        # try retrieval (FAISS or simple)
        match = try_retrieval_agent(faq_json, query)
        if match:
            # match is "Q A" string from corpus; we want the answer part
            # if corpus used "Q A", try to split on question portion
            if "?" in match:
                # split at first '?' and get remainder as answer (best-effort)
                parts = match.split("?", 1)
                answer = parts[1].strip() if len(parts) > 1 else match
            else:
                answer = match
            answer = answer.strip()
            # If the answer contains both Q and A, attempt to find original FAQ and use its 'a'
            for it in faq_json.get("faq", []):
                if (it.get("q","") in match) or (it.get("a","") in match):
                    answer = it.get("a")
                    break
            refined = maybe_refine_with_llm(query, answer, product)
            print("\nAnswer:\n", refined)
            continue

        # no retrieval; try substring fallback
        answer = substring_fallback(faq_json, query)
        if answer:
            refined = maybe_refine_with_llm(query, answer, product)
            print("\nAnswer:\n", refined)
            continue

        print("No good answer found in FAQ. You can try rephrasing the question.")

if __name__ == "__main__":
    # Ensure repo root on PYTHONPATH if running from tools or scripts folder
    root = Path(__file__).resolve().parents[1]
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    interactive_loop()
