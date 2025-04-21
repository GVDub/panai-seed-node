


# PanAI Seed Node — To-Do List

## 🔧 Memory Sync Optimization

- [ ] Tag synced memory with `synced_to:{peer_id}` to avoid re-sending to the same peer
- [ ] Modify sync logic to filter out memories already tagged for that peer
- [ ] Consider cleaning or compressing sync tags (e.g., aggregated tag or metadata object)
- [ ] Cap memory log size or implement log rotation to avoid SSD bloat
- [ ] Add deduplication hash caching to reduce compute on repeated payloads

## 🌐 Open WebUI Integration

- [ ] Investigate Open WebUI Pipeline system as integration layer
- [ ] Prototype a simple pipeline hook that queries PanAI memory API
- [ ] Ensure Pipeline module doesn’t require OWUI fork for deployment
- [ ] Add fallbacks in case PanAI memory API is offline/unreachable

## 🗃️ General Cleanup + Infrastructure

- [ ] Remove unused imports (e.g., `hashlib` if no longer used)
- [ ] Write automated test to verify sync deduplication logic
- [ ] Add logging toggle for debug vs. production use
- [ ] Monitor log size growth over 24–48 hours and report trends
- [ ] Draft optional task-based sync (e.g., via `/sync_once` endpoint)

## 💡 Future Ideas (Pins for Later)

- [ ] Peer-specific sync rate limiting / backoff
- [ ] Dashboard showing which peers have what % of shared memory
- [ ] Support for encrypted memory segments with selective sharing
- [ ] Integration with vector DB for semantic memory routing