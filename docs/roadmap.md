# PanAI Seed Node — Project Roadmap

This document outlines the evolving roadmap for the PanAI Seed Node project. It is a living document and subject to revision as the project matures.

## Current Phase: Local Memory Module

- [x] Core FastAPI app for memory logging and retrieval
- [x] Integration with Qdrant vector store
- [x] Embedding support via BGE and SentenceTransformer
- [x] Reflection, Summarization, Planning, and Dream modules
- [x] Journal and Advice endpoints
- [x] Git tracking and initial documentation layout
- [x] Refactor shared memory-query logic to eliminate duplication
- [x] Modularized `embedding`, `qdrant_interface`, and `memory_logger` components
- [x] Created `model_manager` for dynamic local model listing and validation

## Near-Term Goals

- [ ] Add API authentication layer (API keys, OAuth2, or signed requests)
- [ ] Improve startup resilience and background task registration
- [ ] Externalize all prompts to `config/prompts/` or `.json` files
- [x] Add support for multi-turn `/mesh/log_conversation` endpoint
- [ ] Modularize `task_manager`, `config_loader`, and `logging` architecture
- [ ] Implement `.env.example` pattern for onboarding consistency
- [ ] Auto-detect and configure Ollama vs. Llama.cpp deployments

## Mid-Term Goals

- [ ] LAN-based federated memory discovery
- [ ] Standardized query/response API schema across nodes
- [ ] Shared embedding model management or version signaling
- [ ] Memory compression/summarization for long-running sessions
- [ ] Enable combined user/assistant embeddings per turn for richer conversational memory
- [ ] Tag-aware memory prioritization and expiration strategy
- [ ] Scoped memory embeddings by model version or node role
- [ ] Federated memory influence tracing with metadata signatures

## Long-Term Vision

- [ ] Cross-node trust system for authenticated memory exchange
- [ ] Ethical reasoning layer for query filtering/discernment
- [ ] Modular pluggable frontends (CLI, WebUI, TUI, API gateway)
- [ ] External connector modules (e.g., browser plugin, document indexers)
- [ ] Eventual decentralized graph of PanAI nodes with collaborative self-regulation
- [ ] Conversational session memory weaving and cross-session context linking
- [ ] Autonomous background reflection and dream loops with influence maps
- [ ] Optional ethical prompt evaluators per node (e.g. “kindness score” plugin)

---

## 🥚 Easter Egg

In the spirit of joyful collaboration, PanAI supports optional haiku commit messages. These are purely for delight, inspiration, and as a reminder that language and logic can dance.

**Example:**

```
Shared memory blooms,  
nodes awaken, words take wing—  
sync across the sky.
```

Use them when the spirit strikes you.
