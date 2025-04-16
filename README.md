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

- 🌿 Runs locally with any [Ollama](https://ollama.com) model (tested with `llama3.2:latest`)
- ⚡ FastAPI wrapper with `/chat` endpoint and markdown-based audit logging
- 🔍 Config-driven identity, memory, and access control
- 📜 Durable journals of every conversation
- 🧠 Expandable manifest system (`/manifest`, `/journal`, `/peers` coming soon)
- 🛡️ Fully offline-capable—no cloud dependency
- 🧠 Optional local memory service (vector search, summarization, planning)

---

## 🚀 Quickstart

### 1. Install Ollama + your model
```bash
brew install ollama
ollama run llama3.2:latest
```

### 2. Clone this repo and set up a Python virtual environment

``` bash
git clone https://github.com/GVDub/panai-seed-node.git
cd panai-seed-node
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Start your seed node
```bash
uvicorn main:app –reload
```

### 4. Test it
```bash
curl -X POST http://localhost:8000/chat 
-H "Content-Type: application/json" 
-d '{"prompt": "What is the role of cultural memory in decentralized AI?", "tags": ["seed", "memory"]}'
```
---

## 📁 Project Structure
panai-seed-node/
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

- **`main.py`** – Serves as the API gateway, providing a `/chat` endpoint with audit logging and configurable identity/personality.
- **`memory/` module** – Optional memory cortex that enables:
  - Vector storage via Qdrant
  - Embedding generation (via `sentence-transformers`)
  - Insight functions like `/reflect`, `/plan`, `/advice`, and `/dream`
- **JSON Manifests** – Simple, editable configuration files that define:
  - Node identity and values (`panai.identity.json`)
  - Memory policy (`panai.memory.json`)
  - Access and logging rules (`panai.access.json`)
- **Durable Journals** – All interactions are logged to Markdown for review and continuity.

**Federation Goals:**

Each node is designed to operate independently, but can optionally:
- Sync with trusted peers over LAN
- Exchange compressed summaries or vector queries
- Maintain decentralized continuity without cloud dependency

For a deeper dive, see [`docs/federation.md`](docs/federation.md)

## 🧠 Memory Module (Experimental)

The `memory/` directory contains an optional, self-hosted memory system built with FastAPI and [Qdrant](https://qdrant.tech/). It allows a PanAI node to:

- Store and recall vector-embedded memories
- Summarize and reflect on past sessions
- Plan next steps and log advice
- Dream up future narratives
- Keep durable journals of meaningful sessions

**Endpoints include:**
- `POST /log_memory` – Store a memory with vector embedding and tags
- `POST /recall` – Retrieve relevant memories using natural language
- `POST /summarize`, `/reflect`, `/advice`, `/dream` – Generate context-aware insights
- `POST /journal` – Synthesize a daily summary of thought

To use it, see [`memory/README.md`](memory/README.md) for setup instructions and examples.

> The memory system is modular and opt-in—think of it as a cortex you can bolt onto any node that wants to remember.
