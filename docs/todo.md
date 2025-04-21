# PanAI Seed Node – TODO

## 🔥 Urgent: Memory Sync & Logging

- [x] **Prevent Re-sending Synced Memory**
  - Add `synced_to` field (e.g., list of node IDs or URLs) to each memory entry
  - Skip syncing to nodes already listed
  - Append node to `synced_to` list on success

- [ ] **Tag Synced Memories for Pruning**
  - Append a `synced_to_all_peers` tag when memory has been sent to all active peers
  - Use this tag during pruning to safely remove synced entries

- [ ] **Implement Log Pruning**
  - Define a retention policy: max age, max count, or total size
  - Add config options in `config.yaml` or `.env`
  - Write cleanup function to run periodically or via CLI

- [ ] **Avoid Infinite Reflection Loops**
  - Identify and suppress automatic analysis of reflection-tagged logs
  - Filter out re-analysis of logs already tagged as summaries

- [ ] **Add Logging Controls**
  - Optional log level (`debug`, `info`, etc.)
  - Option to silence low-priority logs or tag them as ephemeral

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

---

## 📦 Open WebUI Integration

- [ ] **Evaluate Pipelines as Entry Point**
  - Explore using Open WebUI Pipelines to connect PanAI without forking
  - Define PanAI memory APIs as pipeline stages (search, recall, write)

- [ ] **Define OpenWebUI Plugin Endpoint Wrappers**
  - Implement `/memory/search`, `/memory/log_memory`, etc., as plugin-callable stages
  - Verify auth context/namespace tagging if used within OWUI sessions

---

## 📎 Cleanup & Refactoring

- [x] **Remove unused imports (`hashlib`, etc.)**
- [ ] **Add `.env.example` with all keys**
- [ ] **Add contributor-style doc section on how to run local multi-node mesh**

