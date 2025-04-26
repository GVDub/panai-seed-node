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

## Near-Term Goals

- [ ] Add authentication layer to API (e.g., API keys or OAuth2)
- [ ] Establish persistent startup and watchdog behavior for system restarts
- [ ] Move endpoint prompts to modular config files
- [ ] Extend memory to support time-based and event-based querying
- [x] Begin local memory-to-memory federation (manual sync)
- [ ] Add support for full conversation logging (multi-turn chat sessions) via `/mesh/log_conversation` endpoint

## Mid-Term Goals

- [ ] LAN-based federated memory discovery
- [ ] Standardized query/response API schema across nodes
- [ ] Shared embedding model management or version signaling
- [ ] Memory compression/summarization for long-running sessions
- [ ] Enable combined user/assistant embeddings per turn for richer conversational memory

## Long-Term Vision

- [ ] Cross-node trust system for authenticated memory exchange
- [ ] Ethical reasoning layer for query filtering/discernment
- [ ] Modular pluggable frontends (CLI, WebUI, TUI, API gateway)
- [ ] External connector modules (e.g., browser plugin, document indexers)
- [ ] Eventual decentralized graph of PanAI nodes with collaborative self-regulation
- [ ] Conversational session memory weaving and cross-session context linking

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
