# src/state/schema.py
from typing import TypedDict, List, Dict, Any, Optional

class PipelineState(TypedDict, total=False):
    # Inputs / core
    raw_input: Dict[str, Any]
    product: Dict[str, Any]
    qa_pairs: List[Dict[str, Any]]
    blocks: Dict[str, Any]
    comparison: Dict[str, Any]

    # Draft / revision cycle
    draft_page: Dict[str, Any]
    critique: Optional[str]
    approved: Optional[bool]

    # Internal bookkeeping
    run_id: Optional[str]
    meta: Optional[Dict[str, Any]]
