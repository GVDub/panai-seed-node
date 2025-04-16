# API Reference

This section documents the available API endpoints for the PanAI Seed Node memory module.

## Base URL

```
http://<your-server-ip>:8000
```

> Replace `<your-server-ip>` with the actual IP address or hostname of your memory node.

## Endpoints

### POST `/log_memory`
Log a new memory entry with embedded vector and optional tags.
- **Request Body**:
  ```json
  {
    "text": "The memory text content.",
    "session_id": "your-session-id",
    "tags": ["tag1", "tag2"]
  }
  ```
- **Response**:
  ```json
  {
    "status": "🧠 Memory logged.",
    "session_id": "your-session-id"
  }
  ```

### POST `/search`
Perform a vector-based search using an embedding.
- **Request Body**:
  ```json
  {
    "vector": [0.01, 0.02, ...],
    "limit": 5
  }
  ```

### POST `/recall`
Recall relevant memory based on natural language input.
- **Request Body**:
  ```json
  {
    "text": "Your query here",
    "limit": 5
  }
  ```

### POST `/search_by_tag`
Retrieve all memory entries matching a specific tag.
- **Request Body**:
  ```json
  {
    "tag": "example-tag",
    "limit": 10
  }
  ```

### POST `/reflect`
Generate a reflection summary based on prior memory entries in a session.

### POST `/advice`
Provide actionable guidance derived from session reflections and logs.

### POST `/plan`
Output a multi-step plan based on the advice or memory context.

### POST `/next`
Suggest the most immediate next action from an ongoing session.

### POST `/dream`
Construct a speculative or creative narrative based on session history.

### POST `/journal`
Create a summarized log of recent session activity in a narrative style.

## Notes

- All endpoints accept and return JSON.
- Ensure `Content-Type: application/json` is included in the request headers.
- Use consistent `session_id` values to group and retrieve related data.
