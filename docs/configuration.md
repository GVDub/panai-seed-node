# Configuration

Each PanAI Seed Node requires minimal but structured configuration to operate securely and coherently within a decentralized network.

## Node Identity

Each node should be uniquely identified with a human-readable name. This is useful for peer-to-peer handshake verification and memory attribution.

Example:
```yaml
node:
  name: "<YOUR_NODE_NAME>"
  description: "This node handles long-term memory and reflection services."
```

## Network Configuration

To allow communication between nodes, you'll define IP addresses and ports for services such as memory APIs, vector stores, and event messaging systems.

Example:
```yaml
network:
  host: "<YOUR_IP_ADDRESS>"
  port: 8000
  peers:
    - name: "Node-A"
      address: "http://<NODE_A_IP>:8000"
    - name: "Node-B"
      address: "http://<NODE_B_IP>:8000"
```

## Memory Storage

Define the vector database (e.g., Qdrant) storage path, embedding model configuration, and collection parameters.

Example:
```yaml
memory:
  database:
    type: "qdrant"
    path: "/mnt/panai-store/qdrant"
  embedding_model:
    name: "BAAI/bge-small-en"
    dimensions: 384
    distance_metric: "cosine"
```

## Service Endpoints

Each memory or processing module (e.g., journal, dream, reflect) can be independently enabled or disabled.

Example:
```yaml
services:
  reflect: true
  dream: true
  journal: true
  advice: true
  plan: true
  summarize: true
```

## API Key and Access Control

Use `.env` files or secret mounting for managing keys and access credentials.

Example `.env` file:
```
OLLAMA_API_BASE_URL=http://localhost:11434
NODE_SECRET_KEY=your-secret-key
```

## Federation Options (Advanced)

For distributed configurations, nodes may optionally broadcast memory events, synchronize via pub/sub (e.g., NATS or MQTT), and register to a peer discovery service.

Example:
```yaml
federation:
  enabled: true
  pubsub:
    provider: "nats"
    endpoint: "nats://<BROKER_IP>:4222"
  discovery:
    service: "consul"
    domain: "panai.local"
```

---

Configurations may be loaded via `config.yaml`, `settings.json`, or passed in as environment variables, depending on your deployment preference. Support for future CLI flags or REST-based dynamic reconfiguration is under consideration.
