# API Specification — AIMeridian

**Version:** 1.0
**Phase:** 0 — Planning
**Last Updated:** 2026-03-12
**Base URL:** `/api/v1`
**Format:** All requests and responses are `application/json`

---

## Conventions

- All IDs are UUIDs
- All timestamps are ISO 8601 UTC strings (`2026-03-12T06:00:00Z`)
- Pagination uses `page` (1-based) and `page_size` (default 20, max 100)
- Errors follow the standard error envelope (see below)
- HTTP 422 is returned for validation errors (Pydantic)

### Standard Response Envelope

**Success (list):**
```json
{
  "data": [...],
  "total": 142,
  "page": 1,
  "page_size": 20
}
```

**Success (single):**
```json
{
  "data": { ... }
}
```

**Error:**
```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Content item not found",
    "detail": null
  }
}
```

---

## Feed

### `GET /api/v1/feed`

Returns ranked, filtered content items. Only items with `status = 'ranked'` are returned.

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | int | 1 | Page number (1-based) |
| `page_size` | int | 20 | Items per page (max 100) |
| `content_type` | `str[]` | all | Filter by type: `paper`, `repo`, `post`, `article`, `model`, `video`, `tool`, `other` |
| `topic_tags` | `str[]` | all | Filter by topic tags (OR within tags, AND across other filters) |
| `source_ids` | `uuid[]` | all | Filter by source IDs |
| `date_from` | `date` | none | Published on or after this date |
| `date_to` | `date` | none | Published on or before this date |
| `min_score` | int | 0 | Minimum relevance score (0–100) |
| `status_filter` | `string` | `unread` | `all` \| `unread` \| `saved` |
| `search_query` | `string` | none | Full-text search across title and summary |
| `sort` | `string` | `relevance` | `relevance` \| `date` \| `score` |

**Response `200 OK`:**
```json
{
  "data": [
    {
      "id": "uuid",
      "title": "Attention Is All You Need: A Retrospective",
      "url": "https://arxiv.org/abs/2401.12345",
      "summary": "This paper revisits the transformer architecture...",
      "content_type": "paper",
      "topic_tags": ["transformers", "attention", "nlp"],
      "author": "Vaswani et al.",
      "published_at": "2026-03-10T00:00:00Z",
      "fetched_at": "2026-03-12T06:00:00Z",
      "relevance_score": 87,
      "source": {
        "id": "uuid",
        "name": "arXiv cs.AI",
        "platform": "arxiv"
      },
      "feedback": {
        "up": false,
        "down": false,
        "saved": false,
        "skipped": false
      },
      "extra": {
        "arxiv_id": "2401.12345"
      }
    }
  ],
  "total": 142,
  "page": 1,
  "page_size": 20
}
```

---

## Sources

### `GET /api/v1/sources`

Returns all sources.

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `status` | `string` | all | `active` \| `paused` \| `archived` \| `trial` |
| `platform` | `string` | all | Filter by platform |
| `category` | `string` | all | Filter by category |

**Response `200 OK`:**
```json
{
  "data": [
    {
      "id": "uuid",
      "name": "arXiv cs.AI",
      "platform": "arxiv",
      "url": "https://arxiv.org",
      "category": "research",
      "description": "AI papers from arXiv cs.AI category",
      "status": "active",
      "rating": 5,
      "fetch_config": { "query": "cs.AI", "max_results": 50 },
      "target_count": 3,
      "created_at": "2026-03-01T00:00:00Z",
      "updated_at": "2026-03-01T00:00:00Z"
    }
  ],
  "total": 12
}
```

---

### `POST /api/v1/sources`

Create a new source.

**Request Body:**
```json
{
  "name": "r/LocalLLaMA",
  "platform": "reddit",
  "url": "https://reddit.com/r/LocalLLaMA",
  "category": "community",
  "description": "Local LLM discussion on Reddit",
  "status": "trial",
  "rating": 3,
  "fetch_config": { "subreddit": "LocalLLaMA" }
}
```

**Response `201 Created`:**
```json
{
  "data": { /* full source object */ }
}
```

---

### `GET /api/v1/sources/{source_id}`

Get a single source with its targets.

**Response `200 OK`:**
```json
{
  "data": {
    "id": "uuid",
    "name": "...",
    "targets": [
      {
        "id": "uuid",
        "name": "cs.AI category",
        "query": "cs.AI",
        "target_type": "topic",
        "status": "active"
      }
    ]
  }
}
```

---

### `PATCH /api/v1/sources/{source_id}`

Update a source (partial update).

**Request Body (all fields optional):**
```json
{
  "name": "arXiv cs.AI + cs.LG",
  "status": "paused",
  "rating": 4,
  "fetch_config": { "query": "cs.AI cs.LG", "max_results": 100 }
}
```

**Response `200 OK`:** Updated source object.

---

### `DELETE /api/v1/sources/{source_id}`

Archive a source (soft delete — sets `status = 'archived'`). Does not delete content already fetched.

**Response `204 No Content`**

---

## Targets

### `GET /api/v1/sources/{source_id}/targets`

List all targets for a source.

**Response `200 OK`:**
```json
{
  "data": [
    {
      "id": "uuid",
      "source_id": "uuid",
      "name": "Andrej Karpathy",
      "handle": "karpathy",
      "query": null,
      "target_type": "person",
      "status": "active",
      "notes": "Former Tesla AI director",
      "created_at": "2026-03-01T00:00:00Z"
    }
  ]
}
```

---

### `POST /api/v1/sources/{source_id}/targets`

Add a new target to a source.

**Request Body:**
```json
{
  "name": "Andrej Karpathy",
  "handle": "karpathy",
  "target_type": "person",
  "status": "active",
  "notes": "Former Tesla AI director"
}
```

**Response `201 Created`:** Full target object.

---

### `PATCH /api/v1/sources/{source_id}/targets/{target_id}`

Update a target.

**Request Body (all fields optional):**
```json
{
  "status": "paused",
  "notes": "Account suspended"
}
```

**Response `200 OK`:** Updated target object.

---

### `DELETE /api/v1/sources/{source_id}/targets/{target_id}`

Archive a target (soft delete — sets `status = 'archived'`).

**Response `204 No Content`**

---

## Feedback

### `POST /api/v1/feedback`

Record a user interaction with a content item.

**Request Body:**
```json
{
  "content_id": "uuid",
  "feedback_type": "up"
}
```

`feedback_type` values: `up` | `down` | `save` | `skip` | `more_like` | `less_like`

**Behaviour:** Upserts — if the same `(content_id, feedback_type)` pair already exists, the existing record is updated (toggled off if sending the same type again).

**Response `201 Created`:**
```json
{
  "data": {
    "id": "uuid",
    "content_id": "uuid",
    "feedback_type": "up",
    "created_at": "2026-03-12T10:00:00Z"
  }
}
```

---

### `DELETE /api/v1/feedback/{feedback_id}`

Remove a feedback record (e.g., undo a thumbs up).

**Response `204 No Content`**

---

## Filter Presets

### `GET /api/v1/filter-presets`

List all saved filter presets.

**Response `200 OK`:**
```json
{
  "data": [
    {
      "id": "uuid",
      "name": "Papers Only",
      "filters": {
        "content_type": ["paper"],
        "min_score": 60
      },
      "is_default": false,
      "created_at": "2026-03-01T00:00:00Z"
    }
  ]
}
```

---

### `POST /api/v1/filter-presets`

Save the current filter state as a named preset.

**Request Body:**
```json
{
  "name": "Papers Only",
  "filters": {
    "content_type": ["paper"],
    "topic_tags": ["llm"],
    "min_score": 60,
    "date_from": null,
    "date_to": null,
    "search_query": null
  },
  "is_default": false
}
```

**Response `201 Created`:** Full preset object.

---

### `PATCH /api/v1/filter-presets/{preset_id}`

Update a preset (rename or change filters).

**Response `200 OK`:** Updated preset object.

---

### `DELETE /api/v1/filter-presets/{preset_id}`

Delete a saved preset.

**Response `204 No Content`**

---

## Preferences

### `GET /api/v1/preferences`

Get all user preferences as a flat key-value map.

**Response `200 OK`:**
```json
{
  "data": {
    "theme": "dark",
    "fetch_cadence": { "cron": "0 6,18 * * *" },
    "notification_keywords": ["GPT-5", "Claude 4"],
    "default_filters": { "content_type": ["paper"], "min_score": 50 },
    "last_visit": "2026-03-12T10:00:00Z",
    "items_per_page": 20
  }
}
```

---

### `PATCH /api/v1/preferences`

Update one or more preferences. Only provided keys are updated (partial update).

**Request Body:**
```json
{
  "theme": "light",
  "notification_keywords": ["GPT-5", "Claude 4", "Gemini 2"]
}
```

**Response `200 OK`:** Full updated preferences map.

---

## Content (Manual Add)

### `POST /api/v1/content/manual`

Manually add a single content item (for LinkedIn links or any URL the user wants to track).

**Request Body:**
```json
{
  "url": "https://www.linkedin.com/posts/...",
  "title": "Anthropic raises Series E",
  "content_type": "article",
  "notes": "LinkedIn post by Dario Amodei"
}
```

**Response `201 Created`:** Full content item object (with `status = 'raw'`; will be summarised on next cycle).

---

## Admin

### `POST /api/v1/admin/trigger-fetch`

Manually trigger the full fetch → summarise → rank pipeline immediately.

**Response `202 Accepted`:**
```json
{
  "data": {
    "job_id": "uuid",
    "status": "queued",
    "message": "Fetch cycle queued. Check logs for progress."
  }
}
```

---

### `GET /api/v1/admin/status`

Get the status of the last scheduler run.

**Response `200 OK`:**
```json
{
  "data": {
    "last_run_at": "2026-03-12T06:00:00Z",
    "last_run_status": "success",
    "items_fetched": 87,
    "items_summarised": 65,
    "items_ranked": 65,
    "errors": [],
    "next_run_at": "2026-03-12T18:00:00Z"
  }
}
```

---

## Health

### `GET /health`

Basic health check (used by Railway, uptime monitor).

**Response `200 OK`:**
```json
{
  "status": "ok",
  "version": "1.0.0"
}
```

---

## Error Codes

| HTTP Status | Code | When |
|-------------|------|------|
| 400 | `BAD_REQUEST` | Malformed request body |
| 404 | `NOT_FOUND` | Resource does not exist |
| 409 | `CONFLICT` | Duplicate content_hash or unique constraint |
| 422 | `VALIDATION_ERROR` | Pydantic validation failure |
| 429 | `RATE_LIMITED` | Too many requests (Phase 5) |
| 500 | `INTERNAL_ERROR` | Unhandled server error |

---

## Pydantic Models (Reference)

```python
# Shared models — full definitions in backend/app/models/

class ContentItem(BaseModel):
    id: UUID
    title: str
    url: str
    summary: str | None
    content_type: ContentType
    topic_tags: list[str]
    author: str | None
    published_at: datetime | None
    fetched_at: datetime
    relevance_score: int | None  # 0–100
    source: SourceSummary
    feedback: FeedbackState
    extra: dict[str, Any]

class Source(BaseModel):
    id: UUID
    name: str
    platform: Platform
    url: str
    category: SourceCategory
    description: str | None
    status: SourceStatus
    rating: int  # 1–5
    fetch_config: dict[str, Any]
    target_count: int
    created_at: datetime
    updated_at: datetime

class FeedbackState(BaseModel):
    up: bool
    down: bool
    saved: bool
    skipped: bool

class FeedQueryParams(BaseModel):
    page: int = 1
    page_size: int = 20
    content_type: list[ContentType] | None = None
    topic_tags: list[str] | None = None
    source_ids: list[UUID] | None = None
    date_from: date | None = None
    date_to: date | None = None
    min_score: int = 0
    status_filter: str = "unread"
    search_query: str | None = None
    sort: str = "relevance"
```
