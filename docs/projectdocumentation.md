# Project: RAG / Agentic Content Generation System
## Problem Statement
Create a modular agentic system that takes a small product dataset and automatically generates structured, machine-readable content pages (FAQ, Product page, Comparison page) without adding new external facts. The system must be modular, reusable, and output JSON.

## Solution Overview
We implemented an orchestrator-driven agentic pipeline in Python. Each agent has a single responsibility:
- ParserAgent: normalizes input
- QAGeneratorAgent: generates categorized Q&A pairs
- ContentBlockAgent: builds reusable content blocks
- ComparisonAgent: creates a fictional product and comparison
- AssemblerAgent: composes page JSON using a template engine

The system emphasizes deterministic rules for traceability, with optional LLM integration points for more natural text generation.

## Scopes & Assumptions
- Input data follows the provided structure (no web lookups)
- No external facts are added; fictional Product B is self-contained and synthetic
- Templates are deterministic JSON mappings
- System demonstrates modular design and is intentionally minimal to show architecture

## System Design
- Orchestrator wires agents in sequence
- Agents are pure (no hidden global state). Inputs/outputs are explicit.
- Template engine maps blocks to structured JSON pages.
- All outputs are saved under `outputs/` as JSON files.

## Diagrams
(Include a simple flow diagram: Input → Parser → QA → ContentBlocks → Comparison → Assembler → Outputs)

## How to run
1. `pip install -r requirements.txt`
2. `python src/main.py`
3. Outputs will be in `outputs/`

## Tests
Run `pytest src/tests` to execute minimal test-suite covering parser, qa, and assembler.

## Design trade-offs
- Deterministic rules were used for correctness and reproducibility.
- LLM usage is optional and can be added as a worker agent for improved copy tone.
