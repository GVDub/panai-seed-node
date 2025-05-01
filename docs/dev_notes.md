# PanAI Developer Notes

## Project Philosophy
- Build modular, maintainable code.
- Prioritize clarity, stability, and extensibility over speed of delivery.
- Design for future distributed, federated systems from the ground up.

## Current Focus Areas
- Heterogeneous model federation: allow nodes to serve different model sets.
- Dynamic model discovery: pull available models from Ollama or other engines.
- Standardized logging: timestamps, levels (INFO, WARNING, ERROR), simple future redirection.
- Progressive modularization: gradually break large monolithic files into logical submodules.
- Centralize configuration loading using `.env` and JSON, with fallback and validation.
- Promote interface-first thinking: design APIs and service layers as swappable contracts.

## In Progress
- Refactoring `memory_api.py` into smaller focused modules.
- Extending `model_manager.py` to support dynamic model registration.
- Planning reflection, dreaming, and ensemble model workflows across heterogeneous nodes.
- Creating internal interfaces for memory, embedding, and model services to improve testability.
- Replacing global/shared state with dependency injection or factory functions.

## Style and Structure Guidelines
- Functions and modules should have clear, single responsibilities.
- All new functions must include a brief docstring (one-liner is fine).
- Use the `log()` helper for all console output (no raw print statements).
- Favor safe fallbacks and graceful error handling whenever possible.
- Use `typing` and `pydantic` models wherever applicable to increase clarity and enforce schema integrity.
- Keep I/O (e.g., filesystem or network access) separated from core logic to ease testing and reuse.
- Organize files by feature domain (e.g., memory, mesh, model) rather than function alone.

## Future Ideas
- Dynamic memory weighting based on reflection feedback.
- Peer-to-peer mesh trust scoring.
- Visual dashboard for federation health and model availability.
- Configurable logging formats and verbosity levels via .env.
- Abstracted `TaskManager` for orchestrating background jobs like sync, reflection, and dreaming.

---

*This document is a living record. Update freely as lessons are learned, ideas evolve, and PanAI grows.*