# src/agents/critique_agent.py
from typing import Dict, Any
from src.state.schema import PipelineState

class CritiqueAgent:
    """
    A deterministic critique agent:
    - Ensures enough QA pairs are present (>= 10)
    - Ensures key blocks exist (benefits_block, usage_block)
    - Sets 'approved' boolean in state and writes feedback to 'critique'
    """

    def run(self, state: PipelineState) -> PipelineState:
        qa_pairs = state.get("qa_pairs") or []
        blocks = state.get("blocks") or {}

        messages = []
        approved = True

        if len(qa_pairs) < 10:
            messages.append(f"Too few QA pairs ({len(qa_pairs)}). Need >= 10.")
            approved = False

        required_blocks = ["benefits_block", "usage_block"]
        for b in required_blocks:
            if b not in blocks:
                messages.append(f"Missing block: {b}")
                approved = False

        if approved:
            messages.append("Critique: OK")
        else:
            messages.append("Critique: Needs revision")

        state["critique"] = " | ".join(messages)
        state["approved"] = approved
        return state
