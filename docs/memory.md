# Memory Module Overview

The PanAI Memory Module provides a persistent, searchable store of conversational and contextual data that can be accessed and evolved over time. It functions as a long-term memory system for AI agents, capturing and retrieving data based on semantic similarity, tags, and session context.

## Purpose

The memory module serves as the cognitive backbone of a PanAI instance, allowing it to:
- Recall relevant prior exchanges
- Reflect on stored information
- Generate advice, summaries, or plans
- Build continuity across sessions

## Architecture

The memory module is implemented as a FastAPI application with endpoints for storing, retrieving, and manipulating memory entries. It uses:
- **Qdrant** as the vector similarity database
- **BAAI/bge-small-en** via `SentenceTransformer` for embedding text
- **Ollama-compatible models** (e.g., `mistral-nemo`) for summarization, reflection, planning, and dreaming

## Services Integration

As of the latest refactor, core functionality has been modularized into a `services` directory. This includes:

- `services/memory.py`: Handles memory logging, embedding, and vector search using Qdrant.
- `services/chat.py`: Manages interaction with local language models via Ollama.
- `services/config.py`: Centralized configuration and environment variable management.
- `services/logger.py`: Shared logger setup for consistent output and debugging.

These services are consumed by the main FastAPI app, enabling easier extension, testing, and eventual integration into a federated PanAI network.

## Key Endpoints

- `POST /log_memory`: Add a new memory to the system
- `POST /search`: Retrieve memories by embedding-based vector similarity
- `POST /recall`: Embed and retrieve based on a text query
- `POST /search_by_tag`: Retrieve memories with matching tags
- `POST /summarize`: Generate a summary of a session
- `POST /reflect`: Produce higher-level reflections across memories
- `POST /advice`: Suggest next actions based on stored memories
- `POST /plan`: Outline a step-by-step approach given a session context
- `POST /dream`: Generate a creative, speculative narrative
- `POST /journal`: Capture a natural-language digest of a session
- `POST /next`: Identify the most important next step

## File Location

The core application code has been modularized and now resides in:
/memory_api/memory_api.py
/services/memory.py

## Future Directions

Planned improvements include:
- Error handling and retry logic for external API calls
- Enhanced prompt templates for better LLM output
- Streamlined utility functions for generating prompts
- Dynamic memory pruning or archiving
- Cross-node memory sharing and federated memory sync

## License

This module is part of the PanAI Seed Node project and is released under the MIT License.
