# kasparro-ai-agentic-content-generation-system-elluru-shaik-arif-azeem

## Overview
Agentic pipeline that converts product data into structured JSON pages (FAQ, Product Page, Comparison) using modular agents and a tiny template engine.

## How to run (local)
1. `pip install -r requirements.txt`
2. `make up`  # runs the pipeline and writes outputs to outputs/
3. `make test`  # runs pytest

## What to submit
- Ensure `docs/projectdocumentation.md` exists (includes design, diagrams).
- Outputs are saved in `outputs/`.
- Repo name must match assignment spec.

## Design notes
- Agents are single-responsibility.
- Deterministic rule-based outputs; LLM/embedding hooks are optional and isolated.
- Each output file contains `_meta` with `run_id` and `timestamp` for traceability.

## Files of interest
- `src/agents/` — agent implementations
- `src/engine/template_engine.py` — simple template engine
- `src/main.py` — orchestrator and CLI entrypoint
- `docs/projectdocumentation.md` — required docs for evaluation
