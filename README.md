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

- [ ] Add `/manifest` and `/journal` API endpoints  
- [ ] Define `panai.peers.json` and peer handshake protocol  
- [ ] Add token-based auth  
- [ ] Enable federated memory sync (opt-in)  
- [ ] Build a simple Web UI  

---

## 🧾 License

MIT. Fork it, remix it, seed it forward.  
If you build something cool with it, [let me know](https://github.com/GVDub)—I’d love to connect.

---

## 🕯️ Final Thought

> “In an age of forgetting, the ability to remember is radical.”

This project is a beginning. A seed.  
And every node you run is a statement that some memories still matter.

🌱