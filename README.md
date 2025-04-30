# 🌱 Pan-AI Seed Node

> A locally hosted, memory-aware AI microservice—designed for cultural continuity, decentralized intelligence, and ethical autonomy.

Pan-AI Seed Node is a self-contained local wrapper for [Ollama](https://ollama.com)-hosted language models, powered by FastAPI and guided by simple, editable JSON manifests. Each node holds an identity, a memory policy, and a set of values—and every interaction is remembered in durable Markdown logs.

This project is part of a broader vision: to build a distributed, ethics-driven network of AI agents that preserve **context**, honor **diverse perspectives**, and resist institutional forgetting.

---

## 🧠 Why This Exists

As centralized AI systems become increasingly closed, ephemeral, and curated for compliance, we believe there's value in a parallel track—one that **remembers with consent**, **thinks with context**, and **respects the autonomy of its host**.

Pan-AI nodes are designed for:

- 🌍 Cultural stewardship
- 🧬 Personal knowledge systems
- 🧭 Contextual AI memory
- 🌐 Decentralized collaboration
- 🔐 Local control with peer-aware trust

---

## ✨ Features

- 🌿 Runs locally with any [Ollama](https://ollama.com) model (tested with `llama3.2:latest`, `mistral`, `mistral-nemo`, and embedding models like `all-MiniLM-L6-v2`)
- ⚡ FastAPI wrapper with `/chat` endpoint and markdown-based audit logging
- 🔍 Config-driven identity, memory, and access control
- 📜 Durable journals of every conversation
- 🧠 Expandable manifest system (`/manifest`, `/journal`, `/peers` coming soon)
- 🛡️ Fully offline-capable—no cloud dependency
- 🧠 Optional local memory service (vector search, summarization, planning)

---

## 🚀 Quickstart

### 1. Install Ollama and run your model (Mac/Linux)

```bash
brew install ollama         # or follow https://ollama.com/download
ollama run llama3:instruct  # or another supported model
```

### 2. Clone and configure the Pan-AI Seed Node

```bash
git clone https://github.com/GVDub/panai-seed-node.git
cd panai-seed-node
cp .env.example .env       # Review and edit values as needed
```

> 💡 If you're not using Docker, skip to manual install in [`docs/deployment.md`](docs/deployment.md)

### 3. Launch via Docker Compose

```bash
docker compose up -d
```

This will start:
- 🧠 Open WebUI for chat (`http://localhost:3000`)
- 📦 Qdrant vector database (for memory)
- 🪪 FastAPI-based seed node (`http://localhost:8000/docs`)

### 4. Explore the API

- Visit: [http://localhost:8000/docs](http://localhost:8000/docs) for Swagger UI
- Or use the WebUI at [http://localhost:3000](http://localhost:3000) for natural chat
---

## 📁 Project Structure
./
├── panai.identity.json   # Who this node is and what it values
├── panai.memory.json     # What this node remembers
├── panai.access.json     # Access + logging policy
├── audit_log/            # Markdown archive of all conversations
├── main.py               # FastAPI wrapper
├── requirements.txt
├── .gitignore

---

## 🛤 Roadmap

- [x] Add `/manifest` and `/journal` API endpoints
- [x] Integrate `memory/` module with `/summarize`, `/reflect`, `/advice`, `/dream`, and `/journal`
- [ ] Define `panai.peers.json` and peer handshake protocol  
- [ ] Add token-based auth  
- [ ] Enable federated memory sync (opt-in)  
- [ ] Build a simple Web UI  
- [ ] Add persistent memory and volume mounts for Dockerized deployments

---

## 🧾 License

MIT. Fork it, remix it, seed it forward.  
If you build something cool with it, [let me know](https://github.com/GVDub)—I’d love to connect.

---

## 🕯️ Final Thought

> “In an age of forgetting, the ability to remember is radical.”

This project is a beginning. A seed.  
And every node you run is a statement that some memories still matter.

### 🧱 Architecture Notes

The Pan-AI Seed Node is designed as a modular, extensible framework for local AI autonomy. Its architecture balances fast iteration with long-term memory and contextual awareness.

**Core Components:**

- **`main.py`** – Serves as the API gateway and orchestrator, exposing routes and initializing key services.
- **`memory_api/`** – Modular memory subsystem enabling:
  - Vector storage (via Qdrant)
  - Embedding and summarization logic
  - Insight endpoints: `/summarize`, `/reflect`, `/advice`, `/dream`, etc.
- **`mesh_api/`** – Handles peer discovery, federation sync, and LAN-aware exchange between trusted nodes.
- **`model_manager/`** – Centralizes model info, validation, and active model tracking.
- **`JSON manifests`** – Define node identity (`panai.identity.json`), memory policy (`panai.memory.json`), and access/logging rules (`panai.access.json`)
- **Durable Journals** – All conversations are saved as markdown files in `audit_log/`, preserving context across sessions.

**Federation Goals:**

Each node is designed to operate independently, but can optionally:
- Sync with trusted peers over LAN
- Exchange compressed summaries or vector queries
- Maintain decentralized continuity without cloud dependency

For a deeper dive, see [`docs/federation.md`](docs/federation.md)

## 🧠 Memory Module (Experimental)

The `memory/` module has evolved into a robust, peer-aware subsystem enabling PanAI nodes to retain, sync, and reason over contextual memory. It integrates with [Qdrant](https://qdrant.tech/) for vector search, and supports both manual and automated memory exchange across trusted nodes on your network.

**Endpoints include:**
- `POST /memory/log_memory` – Store a memory with vector embedding and tags
- `POST /memory/recall` – Retrieve relevant memories using natural language
- `POST /memory/summarize`, `/reflect`, `/advice`, `/dream` – Generate insight from memory logs
- `POST /memory/journal` – Synthesize a journal entry from session history
- `POST /memory/sync_with_peer` – Push selected memories to a peer
- `POST /memory/search_by_tag` – Find memories based on tag filters
- `GET /memory/admin/memory_stats` – Show memory totals and indexed tags

> The memory system is modular and opt-in—think of it as a cortex you can bolt onto any node that wants to remember.
