# Security

The PanAI Seed Node prioritizes local sovereignty, consent-based data sharing, and transparent auditing. This document outlines the current and proposed security measures for maintaining the trust, privacy, and safety of participants in the federated memory and communication ecosystem.

## Goals

- Prevent unauthorized access to local or federated memory
- Ensure secure and auditable data transmission between nodes
- Preserve user consent at all stages of data collection and sharing
- Support both local and federated authentication models

## Current Protections

- **Local Deployment**: Memory and compute remain entirely under the control of the user by default.
- **Qdrant Access**: Memory vector database is not exposed externally unless explicitly configured to be.
- **API Gatekeeping**: Each memory-related API endpoint can be restricted via token or IP-based filtering. API middleware is being modularized to support tiered access control and future audit hooks.

## Planned Features

- **Federated Trust Model**: Nodes authenticate and verify peers using signed identities, with support for Merkle-tree or blockchain-based audit trails for traceable propagation of shared memory.
- **Encryption**: 
  - TLS encryption for all inter-node traffic
  - Optional local disk encryption for memory storage
- **Consent Layers**:
  - Mechanism to explicitly tag which memory entries are shareable and which are strictly private
  - Configurable policy for automatic expiration or redaction of sensitive entries
- **Audit Logging**:
  - Cryptographically verifiable logs of memory access and propagation
  - Optional mirrored append-only logs for compliance and recovery
  - Logs are tagged with `memory_id`, `source_node`, and timestamp metadata for traceability.
  - Future work includes adding zero-knowledge or encrypted metadata propagation for partial federation transparency.
- **Authentication**:
  - JWT, API key, or mutual TLS options for local and remote endpoint protection
  - OAuth2 integration for trusted web clients
  - JWT and API key policies configurable via `.env` and `panai.access.json`.
## Security in Modular Design

As PanAI evolves toward a more modular architecture, each component (e.g., memory interface, model manager, peer sync) will be wrapped in a permission-aware layer. This allows for:

- Fine-grained permissioning of routes and memory types
- Scoped access to model invocation endpoints (e.g., prohibit external access to internal-only LLMs)
- Future support for audit-mode dry runs and "consent previews" for federated actions

## Threat Models Considered

- Unauthorized access to memory (local or remote)
- Data poisoning from malicious or spoofed nodes
- Model prompt injection attempts via shared memory
- Replay attacks or denial-of-service over inter-node APIs

## Security Philosophy

Like all memory, security in PanAI is contextual. Rather than rely on black-box obfuscation, we prioritize:

- Transparency over secrecy
- Intentional sharing over blanket permissions
- Human-readable logs over silent failure

We aim for a system where the user is never surprised by what is remembered, shared, or lost.

Security is not a toggle, but a process integrated at each architectural layer. Modularity enables more robust, composable policies.

---
For implementation notes or to contribute to the security module, see the related [GitHub issues](https://github.com/panai-labs/panai-seed-node/issues) or join the discussion on federation protocols.
