# PanAI Seed Node: Development Guidelines

This guide outlines our best practices for building, organizing, and maintaining the PanAI Seed Node project. These tactics aim to keep the codebase clear, maintainable, and easy for others to contribute to and extend.

---

## 1. Modular Architecture

- Group code by concern:
  - `memory_api/` — memory-specific routing and logic
  - `mesh_api/` — peer registry and discovery
  - `model_manager/` — model availability, caching, refresh
  - `app/` (future) — FastAPI app creation, startup tasks, routing
- Structure within modules:
  - `routers/` — HTTP endpoints
  - `tasks.py` — background services
  - `config.py` — centralized config and constants
  - `utils.py` — stateless helpers

---

## 2. Configuration

- Use a single config loader (`config_loader.py`)
- Read paths, ports, timeouts, and feature flags from `panai.memory.json` or `.env`
- Support overrides via environment variables (Docker/Kubernetes)
- Consider migrating to `pydantic.BaseSettings` for validation and defaults

---

## 3. Logging Standards

- Use Python's `logging` instead of `print(...)`
- Configure logging format once at app startup
- Standard levels: `DEBUG`, `INFO`, `WARNING`, `ERROR`
- Structured log fields encouraged (e.g. `extra={"peer": ..., "model": ...}`)

---

## 4. Dependency Injection & State Management

- Avoid global state: use FastAPI `Depends` or injected service classes
- Qdrant client, embedding models, peer registries → inject rather than hard-code
- Enables testing, mocking, and multiple instance support

---

## 5. Type Hints & Docstrings

- Annotate all functions with input/output types
- Use `Pydantic` models for validation and clarity
- Every module should start with a docstring describing its role
- Every public function/method should explain parameters and returns

---

## 6. Testing & Isolation

- Split I/O logic from core logic (pure functions → testable)
- Parameterize:
  - File paths
  - HTTP clients
  - Clock/timestamps
- Use `pytest` with temp files, mock clients, and fixtures

---

## 7. Async-Aware & Scalable

- Avoid blocking calls (`requests`, file writes) in async contexts
- Use:
  - `httpx.AsyncClient` for network
  - `aiofiles` for async file I/O
- Background tasks should run from a centralized scheduler

---

## 8. Code Style & CI

- Format: `black`, `isort`, `flake8` enforced via `pre-commit`
- Linting: `mypy`, `pyright` for type enforcement
- CI pipeline: lint → type-check → test

---

## 9. Onboarding & Documentation

- README must:
  - Explain architecture
  - Include setup and Quickstart
- Use inline docstrings and comments for intent
- Keep `development.md` current with new practices

---

## 10. Extensibility Patterns

- Follow the **Interface → Implementation → Registration** model
  - Example: Embedding, Memory Store, Peer Discovery, Model APIs
- Encourage swappable services via clear interfaces

---

📌 _These practices will evolve—update this file as our ecosystem grows._