# Journal Module

The journal module serves as a persistent log of experiences, interactions, and events that the AI system has processed. Its purpose is to support long-term memory, continuity, and introspective analysis of past sessions.

## Purpose

The journal captures and stores entries for a given `session_id`, allowing other parts of the memory system—such as reflection, summarization, or advice—to operate on a meaningful timeline of experiences.

## Endpoint

### `POST /journal`

Logs a journal entry for a specific session.

**Request Body:**
```json
{
  "session_id": "2024-04-15-demo",
  "limit": 5
}
```
`limit` is optional; defaults to 5 if omitted. The session must already have memories stored.

**Behavior:**
- Queries up to `limit` memories for the given session.
- Generates a human-readable journal entry summarizing or interpreting the session's content.
- Stores the result as a new memory, tagged with `"journal"` and `"meta"`.

**Response Example:**
```json
{
  "session_id": "2024-04-15-demo",
  "timestamp": "2024-04-15T21:10:00Z",
  "journal": "On April 15th, the memory API was successfully initialized...",
  "tags": ["journal", "meta"]
}
```

## Implementation Notes

- Journals are generated via LLM prompt, typically using the same model used for reflections and dreams (e.g., `mistral-nemo`).
- Journals serve as time-anchored "narrative moments" and are useful for feeding into `/reflect` or `/dream` later.
- Journal entries are embedded and stored in the vector database using the same memory pipeline as other types. They can be filtered or prioritized via tags like `journal`, `meta`, or `summary`.

## Future Considerations

- Add support for daily or rolling summaries across sessions.
- Tag critical insights or anomalies for later review.
- Enable personalized tone and formatting preferences for journal entries.
- Chain journal entries across days or sessions to support continuity and multi-day narrative threads.
