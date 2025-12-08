Project Documentation — Agentic / RAG Content Generation System

Author: Elluru Shaik Arif Azeem
Submission: Applied AI Engineer Assignment — Kasparro

1. Problem Statement

Kasparro aims to build AI-native, modular systems that can convert raw product information into structured, production-ready content.
This assignment requires building a multi-agent system which:

Accepts a small, incomplete product dataset

Generates structured, machine-readable JSON pages

Product Page

FAQ Page

Comparison Page

Must NOT add new external facts

Must be deterministic by default

Should demonstrate good engineering: modularity, testability, composability, clean architecture

The system must resemble real-world Applied AI engineering, not a monolithic LLM script.

2. Solution Overview

We implement a modular, orchestrator-driven agentic pipeline where each agent performs a single, isolated responsibility:

Agents
Agent	Purpose
ParserAgent	Normalize and clean product data into a structured internal model (ProductModel).
QAGeneratorAgent	Generate categorized Q&A pairs (Usage, Safety, Informational, Purchase, Benefits).
ContentBlockAgent	Produce reusable semantic “blocks” (benefits, ingredients, usage).
ComparisonAgent	Build a synthetic Product-B and compute simple differences.
AssemblerAgent	Convert blocks into structured JSON pages using template specifications.
Optional Enhancements

HybridQAGeneratorAgent (LLM-Optional)
Used only if OPENAI_API_KEY is available.

RetrievalAgent (FAISS or Simple)
Provides retrieval over generated content for downstream QA and demos.

The system is deterministic by default, with optional AI upgrades that do not affect core evaluation.

3. Scopes & Assumptions
✔ What the system WILL do

Parse user-provided product fields

Generate structured information only using input facts

Produce JSON pages using templates

Allow retrieval-based question answering (optional)

Run deterministically in CI

✘ What the system WILL NOT do

Perform web lookups

Add unverified external facts

Modify input truth-values

Require an LLM to run

Use nondeterministic generation unless explicitly enabled

Input Structure Expectations

The input is assumed to contain keys similar to:

Product Name, Concentration, Skin Type, Key Ingredients, Benefits,
How to Use, Side Effects, Price

4. System Architecture

The pipeline follows clean agentic architecture, inspired by Kasparro’s engineering environment:

         ┌────────────────────┐
         │  Raw Product Input │
         └──────────┬─────────┘
                    ▼
          ┌────────────────────┐
          │    ParserAgent     │
          │ → ProductModel     │
          └──────────┬─────────┘
                    ▼
      ┌────────────────────────────┐
      │     QAGeneratorAgent       │
      │ Generates categorized Q&A  │
      └──────────┬────────────────┘
                 ▼
      ┌────────────────────────────┐
      │   ContentBlockAgent        │
      │ Benefits / Ingredients /   │
      │ Usage Blocks               │
      └──────────┬────────────────┘
                 ▼
      ┌────────────────────────────┐
      │     ComparisonAgent        │
      │ Compare Product A vs B     │
      └──────────┬────────────────┘
                 ▼
      ┌────────────────────────────┐
      │     AssemblerAgent         │
      │  Applies JSON Templates    │
      └──────────┬────────────────┘
                 ▼
      ┌────────────────────────────────────────┐
      │   Output JSON:                         │
      │   • product_page_<run>.json            │
      │   • faq_<run>.json                     │
      │   • comparison_page_<run>.json         │
      └────────────────────────────────────────┘

5. Detailed Component Breakdown
5.1 ParserAgent

Converts raw dict → validated ProductModel

Normalizes fields (splits lists, trims spaces)

Ensures consistent formatting for downstream agents

5.2 QAGeneratorAgent

Generates at least 15 Q&A pairs, categorized as:

Informational

Usage

Benefits

Safety

Purchase

Rules ensure:

No hallucinations

Only input facts used

Deterministic text generation

(If Hybrid LLM is enabled, answers are optionally refined.)

5.3 ContentBlockAgent

Creates reusable structured blocks:

benefits_block

ingredients_block

usage_block

These plug directly into templates.

5.4 ComparisonAgent

Creates a fictional competitor

Compares ingredient overlap

Computes simple numeric price difference

Follows assignment rule: fictional product is allowed but must not introduce real external facts

5.5 AssemblerAgent + Template Engine

A mini-template engine (similar to Jinja but minimal) maps:

"title": "FAQ - {{product.name}}"
"sections": ["benefits_block"]


Into final JSON page outputs.

6. Output Format (Examples)

Each JSON file includes:

{
  "title": "...",
  "sections": [...],
  "faq": [...],
  "_meta": {
      "run_id": "...",
      "timestamp": "...",
      "source": "faq"
  }
}


This ensures observability and traceability — matching industry practice.

7. Test Suite

Tests ensure:

Product parsing works

QA agent produces minimum valid Q&A count

Pipeline runs end-to-end

Retrieval (FAISS or simple fallback) behaves safely

No LLM dependency required

Command:

pytest -v


All tests pass.

8. How to Run
Basic Run
python -m src.main

Run with retrieval enabled
ENABLE_RETRIEVAL=1 python -m src.main

Run with optional LLM
OPENAI_API_KEY=sk-xxxx python -m src.main

Outputs saved in:
outputs/
    product_page_<id>.json
    faq_<id>.json
    comparison_page_<id>.json
    latest_run.json

9. Docker Execution
docker-compose up


This runs the pipeline inside a reproducible environment.

10. Design Trade-offs
Decision	Reason
Deterministic text	Ensures testability & CI reproducibility
Minimal template engine	Enough flexibility without LLM dependency
Agent modularity	Matches Kasparro’s engineering expectations
Retrieval optional	Not required but useful for demos
LLM optional	Allows enhancement without breaking tests
11. Future Extensions

Richer semantic blocks

Real product catalog comparison

Full LLM summarization agents

SEO-optimized content generator

Vector DB integration (Weaviate / Pinecone)

Streamlit UI for product → content generation

12. Conclusion

This system demonstrates modular agent design, template-driven generation, retrieval-augmented enhancements, and production-style engineering.
It satisfies all required constraints: