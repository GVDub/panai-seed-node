# PanAI Seed Node – TODO

## 🔥 Urgent: Memory Sync & Logging

- [x] **Prevent Re-sending Synced Memory**
  - Add `synced_to` field (e.g., list of node IDs or URLs) to each memory entry
  - Skip syncing to nodes already listed
  - Append node to `synced_to` list on success

- [x] **Tag Synced Memories for Pruning**
  - Append a `synced_to_all_peers` tag when memory has been sent to all active peers
  - Use this tag during pruning to safely remove synced entries

- [ ] **Implement Log Pruning**
  - Define a retention policy: max age, max count, or total size
  - Add config options in `config.yaml` or `.env`
  - Write cleanup function to run periodically or via CLI

- [x] **Avoid Infinite Reflection Loops**
  - Identify and suppress automatic analysis of reflection-tagged logs
  - Filter out re-analysis of logs already tagged as summaries

- [x] **Add Logging Controls**
  - Optional log level (`debug`, `info`, etc.) Fully complete
  - Option to silence low-priority logs or tag them as ephemeral

- [x] **Standardize Logging Across Modules** – Complete for model_manager.py, memory_api.py, and mesh_api.py

---

## ⚙️ Stability & Infrastructure

- [ ] **Finalize Deduplication Logic**
  - Improve content hash or text normalization to catch near-dupes
  - Consider memory TTL for dedupe cache

- [ ] **Tag-Based Routing Rules**
  - Route certain tags (e.g., `mesh`, `reflection`, `sync-test`) only to relevant nodes
  - Support tag-based ignore lists per node

- [ ] **Auto-Sync Timing Controls**
  - Add `min_sync_interval` config to reduce frequency for low-traffic nodes
  - Possibly stagger sync cycles between nodes

- [ ] **Batch Memory Exports to Avoid OOM**
  - Add batch size config for memory export to JSONL
  - Monitor RAM usage and adjust defaults for low-RAM nodes

- [ ] **Migrate to AsyncZeroconf**
  - Replace Zeroconf with AsyncZeroconf for service registration
  - Update startup/shutdown flows to await async unregister
  - Eliminate blocking I/O warning on shutdown

- [ ] **Auto-Create Qdrant Collection If Missing**
  - Add startup check for `panai_memory` collection
  - Create if not found, using configured size/type

- [ ] **Environment-Aware Docker Support**
  - Handle bare-metal Ollama vs Docker container networking
  - Allow override via `.env` and `OLLAMA_BASE_URL`

---

## 📦 Open WebUI Integration

- [ ] **Evaluate Pipelines as Entry Point**
  - Explore using Open WebUI Pipelines to connect PanAI without forking
  - Define PanAI memory APIs as pipeline stages (search, recall, write)

- [ ] **Define OpenWebUI Plugin Endpoint Wrappers**
  - Implement `/memory/search`, `/memory/log_memory`, etc., as plugin-callable stages
  - Verify auth context/namespace tagging if used within OWUI sessions

- [ ] **Preserve Model & API Settings Across Restarts**
  - Investigate persistent Open WebUI volume behavior
  - Possibly include `.webui.env` or documented workaround

---

## 📎 Cleanup & Refactoring

- [x] **Remove unused imports (`hashlib`, etc.)**
- [x] **Add `.env.example` with all keys**
- [ ] **Add contributor-style doc section on how to run local multi-node mesh**
- [x] Modularized memory_api and mesh_api into dedicated components (embedding, logging, config, peer registry, routes, utils)

- [ ] **Finish mesh_api Modularization**
  - `mesh_routes.py`, `peer_registry.py`, `mesh_utils.py` moved and active

- [ ] **Audit and Align All Docs**
  - Ensure `docs/*.md` files reflect current structure and modular design
