# PanAI Memory Module

The `memory` module is a local memory API for the PanAI Seed Node project, designed to enable semantic memory logging, retrieval, reflection, and planning via vector embeddings stored in Qdrant.

## Overview

This module uses:
- **FastAPI** for serving endpoints
- **Qdrant** as a vector database
- **SentenceTransformer** for embeddings (currently using `BAAI/bge-small-en`)
- **Ollama** for local inference and summarization using models like `mistral-nemo`, `llama3`, and `bge-m3`

It allows PanAI to log contextual memories, recall them semantically, reflect on patterns, and even generate dreams and action plans based on stored interactions.

## Endpoints

- `POST /log_memory` — Logs a memory embedding with metadata
- `POST /recall` — Semantic recall of related memory by query text
- `POST /search` — Raw vector similarity search
- `POST /search_by_tag` — Retrieve entries by tag
- `POST /reflect` — Generates a reflection based on past session logs
- `POST /summarize` — Summarizes all logs from a session
- `POST /advice` — Provides advice from past entries
- `POST /plan` — Drafts a step-by-step plan based on advice
- `POST /next` — Determines the next actionable step
- `POST /dream` — Generates a narrative 'dream' of the session's trajectory
- `POST /journal` — Logs a journal entry synthesized from session activity

## Setup

1. Create and activate a Python virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

2. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the API server:
   ```bash
   uvicorn memory_api:app --host 0.0.0.0 --port 8000
   ```

4. Ensure Qdrant and Ollama are running with the appropriate models loaded.

## Notes

- All memory entries are stored in a Qdrant collection named `panai_memory`.
- Embeddings are normalized to ensure cosine similarity performs optimally.
- This module is intended to run locally as part of a trusted, privacy-focused AI infrastructure.

---

This is the thinking cortex of PanAI—where memory, pattern, and purpose converge.
