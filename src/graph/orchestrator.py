# src/graph/orchestrator.py
from typing import Dict, Any
import uuid
from src.graph.state_graph import StateGraph
from src.state.schema import PipelineState
from src.agents.parser_agent import ParserAgent
from src.agents.qa_agent import QAGeneratorAgent
from src.agents.content_block_agent import ContentBlockAgent
from src.agents.comparison_agent import ComparisonAgent
from src.agents.assembler_agent import AssemblerAgent
from src.agents.critique_agent import CritiqueAgent

def _wrap_agent_run(agent):
    def node_fn(state: Dict[str, Any]) -> Dict[str, Any]:
        # each agent expects particular inputs and returns updates via state
        # we call agent.run and then merge returned dict (or rely on agent mutating)
        result = agent.run(state.get("raw_input") if hasattr(agent, "run") and agent.__class__.__name__ == "ParserAgent" else state)
        # agent.run may return ProductModel or lists; convert to state entries
        # allow agents to return dict-like state fragments
        if isinstance(result, dict):
            # Merge common known outputs heuristically
            # Parser returns ProductModel-like (dict)
            if "name" in result or "Product Name" in result:
                state["product"] = result
            elif "title" in result and ("faq" in result or "sections" in result):
                state["draft_page"] = result
            elif "comparison" in result or "price_inr" in result:
                state["comparison"] = result
            else:
                # if it's a block mapping
                # we simply set 'blocks' if keys look like blocks
                if any(k.endswith("_block") for k in result.keys()):
                    state.setdefault("blocks", {}).update(result)
                else:
                    # fallback: merge directly
                    state.update(result)
        else:
            # if agent returned None, we assume it mutated state in place
            pass
        return state

    return node_fn

def build_graph(use_hybrid_qa: bool = False) -> StateGraph:
    graph = StateGraph()

    # instantiate agents
    parser = ParserAgent()
    qa = QAGeneratorAgent() if not use_hybrid_qa else __import__("src.agents.llm_qa_agent", fromlist=["HybridQAGeneratorAgent"]).HybridQAGeneratorAgent()
    content = ContentBlockAgent()
    critique = CritiqueAgent()
    comparison = ComparisonAgent()
    assembler = AssemblerAgent()

    # add nodes (wrapped)
    graph.add_node("parser", lambda s: {**s, "product": parser.run(s.get("raw_input") or s)})
    graph.add_node("qa", lambda s: {**s, "qa_pairs": qa.run(s.get("product"))})
    graph.add_node("content", lambda s: {**s, "blocks": content.run(s.get("product"))})
    graph.add_node("critique", lambda s: critique.run(s))
    graph.add_node("comparison", lambda s: {**s, "comparison": comparison.run(s.get("product"))})
    graph.add_node("assembler", lambda s: {**s, "draft_page": assembler.run(s.get("product"), s.get("blocks"), s.get("qa_pairs"), s.get("comparison"), {
        "product": {"title":"{{product.name}}", "sections":["benefits_block","ingredients_block","usage_block"], "include_faq": False},
        "faq": {"title":"FAQ - {{product.name}}", "sections":[], "include_faq": True},
        "comparison": {"title":"Comparison - {{product.name}} vs Fictional", "sections":["ingredients_block"], "include_faq": False}
    })})

    # linear edges
    graph.add_edge("parser", "qa")
    graph.add_edge("qa", "content")
    graph.add_edge("content", "critique")

    # conditional: critique decides next node (loop back or proceed)
    def critique_decision(state: Dict[str, Any]) -> str:
        approved = state.get("approved", False)
        if approved:
            return "comparison"
        else:
            # loop back to 'qa' for revision
            return "qa"

    graph.add_conditional_edge("critique", critique_decision)

    graph.add_edge("comparison", "assembler")
    graph.set_end("assembler")

    return graph

def run_graph(raw_input: Dict[str, Any], dry_run: bool = False, use_hybrid_qa: bool = False) -> Dict[str, Any]:
    graph = build_graph(use_hybrid_qa=use_hybrid_qa)
    initial_state: PipelineState = {"raw_input": raw_input, "run_id": str(uuid.uuid4()), "approved": False}
    final_state = graph.invoke(initial_state)
    # optionally write outputs here or return final_state
    return final_state
