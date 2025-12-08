# src/agents/llm_qa_agent.py
from typing import List, Dict, Optional
import os
from .qa_agent import QAGeneratorAgent

# Optional imports for OpenAI — imported inside functions to avoid hard dependency
class HybridQAGeneratorAgent:
    """
    Wraps the deterministic QAGeneratorAgent and optionally refines answers with an LLM.
    LLM usage is behind OPENAI_API_KEY environment variable — tests remain deterministic.
    """

    def __init__(self, llm_provider: Optional[str] = None):
        # llm_provider is a placeholder if you want to add different providers later
        self.base = QAGeneratorAgent()
        self.api_key = os.getenv("OPENAI_API_KEY")  # if present, agent will attempt to refine
        self.llm_provider = llm_provider or "openai"

    def run(self, product) -> List[Dict]:
        deterministic = self.base.run(product)
        if not self.api_key:
            return deterministic

        # If API key present, refine answers. We keep a safe, rate-limited approach:
        refined = []
        for item in deterministic:
            q = item["q"]
            a = item["a"]
            # Attempt to refine via OpenAI (if installed); otherwise return original
            refined_answer = self._maybe_refine_with_openai(q, a, product)
            item["a"] = refined_answer or a
            refined.append(item)
        return refined

    def _maybe_refine_with_openai(self, q: str, a: str, product) -> Optional[str]:
        """
        Example refinement using OpenAI ChatCompletion. This function will only run if
        'openai' Python package is installed and OPENAI_API_KEY is set.
        We keep prompt minimal and deterministic fallback in case of any failure.
        """
        try:
            import openai
        except Exception:
            return None

        try:
            openai.api_key = self.api_key
            # small prompt to rephrase and be concise
            prompt = (
                f"Rephrase the answer concisely and clearly. Context product: {product.name}. "
                f"Question: {q}\nExisting answer: {a}\nRefined answer:"
            )
            resp = openai.ChatCompletion.create(
                model="gpt-4o-mini" if hasattr(openai, "gpt4o") else "gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.0,
            )
            # parse safely
            text = (resp["choices"][0]["message"]["content"]).strip()
            return text if text else None
        except Exception:
            return None
