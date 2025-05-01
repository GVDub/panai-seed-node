# Manual Memory Entry Guide

This document outlines the process for manually logging a memory to the PanAI memory system via the `/log_memory` endpoint. This is useful for entering key insights, quotes, or conceptual seeds that should persist in the system.

---

## 📥 API Endpoint

**POST** `/log_memory`

This route accepts both ephemeral and persistent memories depending on server config.

### Required JSON fields:

- `text` (string): The memory content you want to log.
- `session_id` (string) (optional): A unique identifier to group related memories. You can reuse a session or create a new one. If omitted, a timestamp-based session will be generated.
- `tags` (list of strings): Keywords or topics that help categorize and retrieve the memory later. This can be empty but is strongly recommended.

---

## 🧠 Example

Here’s an example of a manually entered philosophical axiom that was logged via this process:

```json
{
  "text": "That which is forgotten still exerts force.\nSo does that which is yet undiscovered.\n\nTogether, they feel like the axioms of PanAI’s worldview—maybe even the first two entries in its evolving Credo or Founder’s Scroll. Not rules. Not laws. Just recognitions of weight.",
  "session_id": "2024-04-16-credo",
  "tags": ["philosophy", "credo", "axiom", "panai"]
}
```

---

## 🔄 How to Submit

You can enter the memory manually in two ways:

### Using Swagger UI

1. Open `http://localhost:8000/docs`
2. Find the `POST /log_memory` section
3. Click **"Try it out"**
4. Paste your JSON payload into the request body
5. Click **"Execute"**
6. If the memory was logged successfully, you’ll see a confirmation response with `status: success` and the memory's internal ID.

### Using cURL (terminal)

```bash
curl -X POST http://localhost:8000/log_memory \
  -H "Content-Type: application/json" \
  -d '{
    "text": "That which is forgotten still exerts force.\nSo does that which is yet undiscovered.\n\nTogether, they feel like the axioms of PanAI’s worldview—maybe even the first two entries in its evolving Credo or Founder’s Scroll. Not rules. Not laws. Just recognitions of weight.",
    "session_id": "2024-04-16-credo",
    "tags": ["philosophy", "credo", "axiom", "panai"]
  }'
```

---

## 📌 Tips

- **Use session IDs** like `YYYY-MM-DD-topic` to help organize memory logs chronologically or by theme.
- **Tag thoroughly** to improve retrieval via `/search_by_tag`.
- **Avoid duplicate IDs**: A unique `id` will be generated automatically using timestamp logic.
- Entries logged this way are stored using the same embedding model and pipeline as live interactions.
- If the system supports reflection or dreaming, tagged manual entries may influence future thought loops.

This method ensures persistence of critical insights and creates a durable thought trail.

---

## 🔮 Future Possibilities

- Manual entries could include `importance` or `urgency` flags to influence prioritization.
- Optionally mark memories as `public` or `private` for federated sharing logic.
- Enable journaling modes that auto-tag entries as `meta`, `review`, or `summary`.
