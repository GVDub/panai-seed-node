# Federation Architecture for PanAI Seed Nodes

## Purpose

This document outlines the architecture, goals, and key components required to enable secure, decentralized memory and knowledge sharing across federated PanAI nodes.

## 1. Goals of Federation

- Enable nodes to share selected memory or metadata with trusted peers
- Maintain autonomy, control, and privacy per node
- Build a scalable, self-healing, trust-aware network of AI agents
- Resist institutional forgetting and central points of failure

## 2. Core Concepts

### Node
A self-contained PanAI instance with memory storage, a local model, and API endpoints.

### Session
A logical container for context, associated memories, and related metadata.

### Memory Types
- **Searchable** – Embedded and indexed in Qdrant for semantic retrieval
- **Ephemeral** – In-memory only; discarded after use
- **Private** – Visible only to the originating node
- **Public** – Eligible for federated sharing based on trust policies

### Trusted Peer
Another PanAI node authenticated and authorized to share data.

## 3. Discovery & Trust

- **Discovery Mechanisms**: Static peer list, mDNS, or service registries (e.g., Consul)
- **Authentication**: API keys, OAuth2, mutual TLS, or blockchain-based trust tokens
- **Trust Graph**: Optional blockchain or DAG for identity and auditability

## 4. Federation API Endpoints (Proposed)

- `GET /export_memories?session_id=xyz&tags=...`
  - Returns memory entries with specified filters
- `POST /import_memories`
  - Receives new memories (structured format TBD)
- `POST /announce_presence`
  - Beacon endpoint for announcing availability
- `GET /peer_info`
  - Returns identity, capabilities, and status of the peer node

- Note: All federated requests should support `Authorization` headers for peer validation.

## 5. Shared Memory Format

All shared memories should conform to a common schema:

```json
{
  "memory_id": "uuid",
  "text": "memory text",
  "embedding_vector": [0.12, 0.44, ...],
  "timestamp": "2025-04-15T15:22:00Z",
  "tags": ["reflection", "remote"],
  "session_id": "remote-session-id",
  "source_node": "node_fingerprint_or_url",
  "embedding_model": "recommended_field",
  "privacy_level": "recommended_field",
  "signature": "optional_field"
}
```

- Required fields: `memory_id`, `text`, `embedding_vector`, `timestamp`, `tags`, `session_id`, `source_node`
- Recommended fields: `embedding_model`, `privacy_level`
- Optional fields: `signature`

## 6. Security & Privacy

- Encrypted in transit (TLS)
- Configurable export filters (by tag, timestamp, session_id)
- Optional redaction of sensitive memory fields
- Peer authentication via shared secrets, keys, or trust token exchange
- Logging and audit trails for memory exchanges
- Recommend rotating trust tokens or API keys periodically
- Federation policy enforcement (e.g., max memories per sync, rate limits)

## 7. Future Directions

- Task sharing between nodes
- Federated summarization and journal synthesis
- Trust score computation for shared content
- Optional blockchain/DAG integration for:
  - Identity verification
  - Consent ledger
  - Memory provenance and auditability
- Adaptive peer throttling and memory prioritization based on bandwidth or trust level
- Federated vector routing (memory can be relayed through intermediary nodes if direct connection fails)
