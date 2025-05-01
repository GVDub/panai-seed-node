# API Reference

This section documents the available API endpoints for the PanAI Seed Node memory module.

## Base URL

```
http://<your-server-ip>:8000
```

> Replace `<your-server-ip>` with the actual IP address or hostname of your memory node.

## Headers

All endpoints accept and return JSON. Requests must include:

```http
Content-Type: application/json
```

Authentication is not currently required but may be added later.

## Status Codes

- `200 OK`: Successful operation
- `400 Bad Request`: Invalid input data
- `500 Internal Server Error`: Something went wrong on the server

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
- **Response**:
  ```json
  {
    "results": [
      {
        "text": "Relevant memory entry text",
        "score": 0.98,
        "tags": ["example"]
      }
    ]
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
- **Response**:
  ```json
  {
    "matches": [
      {
        "text": "Closest semantic match text",
        "score": 0.95,
        "session_id": "your-session-id"
      }
    ]
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
- **Response**:
  ```json
  {
    "entries": [
      {
        "text": "Memory text tagged with 'example-tag'",
        "session_id": "tagged-session-id"
      }
    ]
  }
  ```

### POST `/reflect`
Generate a reflection summary based on prior memory entries in a session.
- **Request Body**:
  ```json
  {
    "session_id": "your-session-id"
  }
  ```
- **Response**:
  ```json
  {
    "reflection": "Summary of key ideas and emotional tone"
  }
  ```

### POST `/advice`
Provide actionable guidance derived from session reflections and logs.
- **Request Body**:
  ```json
  {
    "session_id": "your-session-id"
  }
  ```
- **Response**:
  ```json
  {
    "advice": "Suggested actionable steps or considerations"
  }
  ```

### POST `/plan`
Output a multi-step plan based on the advice or memory context.
- **Request Body**:
  ```json
  {
    "session_id": "your-session-id"
  }
  ```
- **Response**:
  ```json
  {
    "plan": [
      "Step 1: Do something",
      "Step 2: Reflect and adapt",
      "Step 3: Continue progress"
    ]
  }
  ```

### POST `/next`
Suggest the most immediate next action from an ongoing session.
- **Request Body**:
  ```json
  {
    "session_id": "your-session-id"
  }
  ```
- **Response**:
  ```json
  {
    "next_action": "Reach out to collaborator with update"
  }
  ```

### POST `/dream`
Construct a speculative or creative narrative based on session history.
- **Request Body**:
  ```json
  {
    "session_id": "your-session-id"
  }
  ```
- **Response**:
  ```json
  {
    "dream": "In a world where memory is shared, you begin to..."
  }
  ```

### POST `/journal`
Create a summarized log of recent session activity in a narrative style.
- **Request Body**:
  ```json
  {
    "session_id": "your-session-id"
  }
  ```
- **Response**:
  ```json
  {
    "journal": "Today you explored the intersection of planning and dreaming..."
  }
  ```
