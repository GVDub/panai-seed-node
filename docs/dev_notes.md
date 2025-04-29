


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

## In Progress
- Refactoring `memory_api.py` into smaller focused modules.
- Extending `model_manager.py` to support dynamic model registration.
- Planning reflection, dreaming, and ensemble model workflows across heterogeneous nodes.

## Style and Structure Guidelines
- Functions and modules should have clear, single responsibilities.
- All new functions must include a brief docstring (one-liner is fine).
- Use the `log()` helper for all console output (no raw print statements).
- Favor safe fallbacks and graceful error handling whenever possible.

## Future Ideas
- Dynamic memory weighting based on reflection feedback.
- Peer-to-peer mesh trust scoring.
- Visual dashboard for federation health and model availability.

---

*This document is a living record. Update freely as lessons are learned, ideas evolve, and PanAI grows.*