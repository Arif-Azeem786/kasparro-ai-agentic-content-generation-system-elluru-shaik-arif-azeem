**Kasparro Agentic Content Generation System — Elluru Shaik Arif Azeem

A modular Applied AI / Agentic Content Generation System that converts raw product data into structured JSON outputs (Product Page, FAQ Page, Comparison Page) using deterministic agents, a lightweight templating engine, and optional retrieval/LLM enhancements.

This project is built according to Kasparro’s engineering expectations — modularity, clarity, extensibility, testability, and deterministic behavior by default.

⭐ Features

Parser Agent converts messy input → normalized ProductModel

QA Generator Agent produces structured Q/A pairs

Content Block Agent generates sections (benefits, ingredients, usage)

Comparison Agent generates basic competitor comparison

Assembler Agent + template engine produce final JSON pages:

product_page.json

faq.json

comparison_page.json

Retrieval Support

FAISS-based retrieval (fast, semantic)

Simple fallback retrieval (bag-of-words)

Optional Hybrid QA (LLM-powered) — enabled only if OPENAI_API_KEY is set

Deterministic Pipeline for CI and evaluation

Full Test Suite (pytest)

Dockerized for reproducible execution

Interactive QA Interface using generated FAQ

📂 Repository Structure
.
├── src/
│   ├── agents/                   # Parser, QA, ContentBlock, Comparison, Assembler, Retrieval agents
│   ├── engine/                   # Tiny template engine & utils
│   ├── models/                   # Pydantic ProductModel
│   ├── templates/                # JSON templates + spec
│   └── main.py                   # Orchestrator pipeline entrypoint
│
├── src/tests/                    # Pytest test suite
│
├── outputs/                      # Generated JSON outputs (auto-created)
│
├── scripts/                      # query_demo.py, interactive_qa.py
│
├── docs/                         # architecture & documentation
├── .github/workflows/ci.yml      # CI pipeline with deterministic execution
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── Makefile
└── README.md

🚀 How to Run Locally
1. Create + activate virtual environment

Windows PowerShell

python -m venv venv
.\venv\Scripts\Activate.ps1


Linux / macOS

python3 -m venv venv
source venv/bin/activate

2. Install dependencies
pip install -r requirements.txt

3. Run the pipeline

This generates product page, FAQ page, and comparison page inside outputs/.

python -m src.main


To run without writing files:

python -m src.main --dry-run

4. Run the test suite
pytest -v


All tests should pass deterministically.

💬 Demos
FAQ & Retrieval Demo
python scripts/query_demo.py

Interactive QA Mode

Ask questions against the generated FAQ using retrieval:

python scripts/interactive_qa.py


Example questions:

How to use the product?

What is the concentration?

Is it suitable for oily skin?

🔍 Retrieval Modes
Mode	How to Enable	Behavior
Deterministic (default)	No env vars	No retrieval, rule-based QA only
Retrieval (FAISS)	ENABLE_RETRIEVAL=1	Semantic search using FAISS index
Retrieval (Simple Fallback)	Automatic	Bag-of-words cosine similarity
Hybrid LLM QA	OPENAI_API_KEY="sk-..."	Refines answers through LLM

Example:

$env:ENABLE_RETRIEVAL="1"
$env:OPENAI_API_KEY="sk-xxxx"
python scripts/interactive_qa.py

🧱 Design Principles
✔ Modular Agents

Each agent handles exactly one responsibility.

✔ Template-driven Output

Assembler + templates → predictable, testable JSON.

✔ Deterministic by Default

Required for CI and reproducibility.

✔ Optional LLM Hooks

LLM refinement is isolated behind environment variables.

✔ Traceability

Every generated file includes:

"_meta": {
  "run_id": "...",
  "timestamp": "...",
  "source": "faq / product_page / comparison_page"
}

🧪 CI Pipeline (GitHub Actions)

The CI workflow:

installs dependencies

runs tests

runs a dry agentic pipeline

disables retrieval/LLM features

enforces deterministic output

Located at:

.github/workflows/ci.yml

🐳 Docker Usage
Build & Run
docker-compose build
docker-compose up --abort-on-container-exit


Default docker env:

ENABLE_RETRIEVAL=0
OPENAI_API_KEY=""

📝 Project Documentation

Full architecture explanation, diagrams, and design choices are located in:

docs/projectdocumentation.md


This document is required for Kasparro evaluation.

✔ Submission Checklist (Kasparro-ready)

Before submitting, ensure:

 Repo name follows required naming format

 README.md is polished (this file)

 docs/projectdocumentation.md exists

 Tests pass (pytest -v)

 CI passes on GitHub

 Pipeline runs without errors

 All outputs generated in outputs/

 No API keys committed

🙌 Author

Elluru Shaik Arif Azeem
Applied AI Engineer — Assignment Submission for Kasparro**
