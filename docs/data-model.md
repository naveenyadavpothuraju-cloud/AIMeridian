# Data Model — AIMeridian

**Version:** 1.0
**Phase:** 0 — Planning
**Last Updated:** 2026-03-12

---

## Overview

Six tables cover all data needs through Phase 5. All tables use UUID primary keys. Timestamps are stored as `TIMESTAMPTZ` (UTC). Phase 4 adds `user_id` foreign keys and RLS policies to the per-user tables.

---

## Entity Relationship Diagram

```
sources (1) ──────────────────── (N) targets
   │                                     │
   │                                     │
   └──────── (N) content (N) ───────────┘
                   │
                   │ (1)
                   │
                (N) feedback

preferences   (standalone, per-user in Phase 4)
filter_presets (standalone, per-user in Phase 4)
```

---

## Table: `sources`

Represents a platform or website we fetch content from (e.g., arXiv, GitHub, Reddit).

```sql
CREATE TABLE sources (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name          TEXT NOT NULL,
  platform      TEXT NOT NULL,           -- 'arxiv' | 'github' | 'reddit' | 'hackernews'
                                         -- | 'huggingface' | 'paperswithcode' | 'rss'
                                         -- | 'twitter' | 'linkedin' | 'youtube' | 'other'
  url           TEXT NOT NULL,           -- Canonical URL of the source
  category      TEXT NOT NULL,           -- 'research' | 'tools' | 'industry' | 'community'
                                         -- | 'newsletter' | 'social'
  description   TEXT,
  status        TEXT NOT NULL DEFAULT 'active',
                                         -- 'active' | 'paused' | 'archived' | 'trial'
  rating        SMALLINT NOT NULL DEFAULT 3 CHECK (rating BETWEEN 1 AND 5),
  fetch_config  JSONB NOT NULL DEFAULT '{}',
                                         -- Platform-specific config:
                                         -- { "query": "cs.AI", "max_results": 50 }     (arXiv)
                                         -- { "org": "anthropics", "topics": ["llm"] }  (GitHub)
                                         -- { "subreddit": "MachineLearning" }          (Reddit)
                                         -- { "feed_url": "https://..." }               (RSS)
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_sources_status    ON sources(status);
CREATE INDEX idx_sources_platform  ON sources(platform);
CREATE INDEX idx_sources_category  ON sources(category);
```

**Notes:**
- `rating` (1–5) influences the ranking weight. Sources rated ≤ 2 are auto-paused.
- `fetch_config` is intentionally flexible JSONB to accommodate per-platform options.
- `status = 'trial'` means content appears in a separate "New Sources" section, not the main feed.

---

## Table: `targets`

A specific entity within a source to track (e.g., a subreddit, a GitHub org, a person's handle, a search query).

```sql
CREATE TABLE targets (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  source_id     UUID NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
  name          TEXT NOT NULL,           -- Human-readable label, e.g. "Andrej Karpathy"
  handle        TEXT,                    -- Twitter handle, GitHub username, subreddit name
  query         TEXT,                    -- Search query string (arXiv, HN, GitHub topics)
  target_type   TEXT NOT NULL,           -- 'person' | 'org' | 'topic' | 'keyword' | 'feed'
  status        TEXT NOT NULL DEFAULT 'active',
                                         -- 'active' | 'paused' | 'archived'
  notes         TEXT,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_targets_source_id ON targets(source_id);
CREATE INDEX idx_targets_status    ON targets(status);
```

**Notes:**
- A `source` can have many `targets`. For example, the Reddit source has targets for `r/MachineLearning`, `r/LocalLLaMA`, etc.
- `handle` and `query` are both optional; which one is used depends on the fetcher for that platform.

---

## Table: `content`

Stores individual fetched items (papers, repos, posts, articles).

```sql
CREATE TABLE content (
  id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  source_id        UUID NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
  target_id        UUID REFERENCES targets(id) ON DELETE SET NULL,
  title            TEXT NOT NULL,
  url              TEXT NOT NULL,
  content_hash     TEXT NOT NULL UNIQUE,  -- SHA-256 of (title + url) for deduplication
  raw_text         TEXT,                  -- Original abstract / description (capped at 2000 chars)
  summary          TEXT,                  -- LLM-generated 2–3 sentence summary
  published_at     TIMESTAMPTZ,           -- Original publish date from source
  fetched_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
  status           TEXT NOT NULL DEFAULT 'raw',
                                          -- 'raw' | 'summarised' | 'ranked' | 'failed'
  relevance_score  SMALLINT,              -- 0–100, set by ranker
  content_type     TEXT NOT NULL DEFAULT 'article',
                                          -- 'paper' | 'repo' | 'post' | 'article'
                                          -- | 'model' | 'video' | 'tool' | 'other'
  topic_tags       TEXT[] NOT NULL DEFAULT '{}',
                                          -- LLM-inferred tags e.g. ['llm', 'fine-tuning']
  author           TEXT,                  -- Author or submitter name
  extra            JSONB NOT NULL DEFAULT '{}',
                                          -- Platform-specific extras:
                                          -- { "stars": 1200, "language": "Python" }  (GitHub)
                                          -- { "score": 342, "comments": 87 }         (HN)
                                          -- { "arxiv_id": "2401.12345" }             (arXiv)
  created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Deduplication (primary)
CREATE UNIQUE INDEX idx_content_hash           ON content(content_hash);

-- Feed query performance
CREATE INDEX idx_content_published_at          ON content(published_at DESC);
CREATE INDEX idx_content_status                ON content(status);
CREATE INDEX idx_content_source_id             ON content(source_id);
CREATE INDEX idx_content_relevance_score       ON content(relevance_score DESC);
CREATE INDEX idx_content_content_type          ON content(content_type);

-- Full-text search
ALTER TABLE content ADD COLUMN fts TSVECTOR
  GENERATED ALWAYS AS (
    to_tsvector('english', coalesce(title, '') || ' ' || coalesce(summary, '') || ' ' || coalesce(raw_text, ''))
  ) STORED;
CREATE INDEX idx_content_fts ON content USING GIN(fts);
```

**Notes:**
- `content_hash` = `sha256(title + url)`. Prevents storing duplicate items across fetch cycles.
- `raw_text` is stored (capped at 2000 chars) only to enable re-summarisation if the prompt changes. Not displayed to the user.
- `topic_tags` is a plain text array for fast filtering. Tags are inferred by the summariser or ranker.
- `extra` JSONB stores platform-specific metadata without needing schema changes.
- The `fts` generated column powers keyword search without a separate search service.

---

## Table: `feedback`

Stores user interactions with content items.

```sql
CREATE TABLE feedback (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  content_id      UUID NOT NULL REFERENCES content(id) ON DELETE CASCADE,
  feedback_type   TEXT NOT NULL,
                                   -- 'up' | 'down' | 'save' | 'skip' | 'more_like' | 'less_like'
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- One feedback type per content item (upsert-friendly)
CREATE UNIQUE INDEX idx_feedback_content_type ON feedback(content_id, feedback_type);

CREATE INDEX idx_feedback_content_id     ON feedback(content_id);
CREATE INDEX idx_feedback_type           ON feedback(feedback_type);
CREATE INDEX idx_feedback_created_at     ON feedback(created_at DESC);
```

**Notes:**
- The unique index on `(content_id, feedback_type)` means a user can have at most one of each type per item (e.g., only one "up" signal per item). Use `INSERT … ON CONFLICT DO UPDATE` to toggle.
- In Phase 4, a `user_id` column is added and the unique index becomes `(user_id, content_id, feedback_type)`.

---

## Table: `preferences`

Key-value store for user settings.

```sql
CREATE TABLE preferences (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  key         TEXT NOT NULL UNIQUE,
  value       JSONB NOT NULL,
  updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Well-known keys and their value shapes:
-- 'theme'              → "dark" | "light" | "system"
-- 'fetch_cadence'      → { "cron": "0 6,18 * * *" }
-- 'notification_keywords' → ["GPT-5", "Claude 4", "Gemini 2"]
-- 'default_filters'    → { "content_type": ["paper"], "min_score": 50 }
-- 'last_visit'         → "2026-03-12T10:00:00Z"
-- 'items_per_page'     → 20
```

**Notes:**
- In Phase 4, a `user_id` column replaces the single-user key-value approach.
- Prefer JSONB values over multiple columns to avoid schema migrations for every new preference.

---

## Table: `filter_presets`

Named, saved filter combinations.

```sql
CREATE TABLE filter_presets (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name        TEXT NOT NULL,
  filters     JSONB NOT NULL,
              -- Shape:
              -- {
              --   "content_type": ["paper", "repo"],
              --   "topic_tags": ["llm", "fine-tuning"],
              --   "source_ids": ["uuid1", "uuid2"],
              --   "date_from": "2026-01-01",
              --   "date_to": null,
              --   "min_score": 60,
              --   "status": "unread",
              --   "search_query": "multimodal"
              -- }
  is_default  BOOLEAN NOT NULL DEFAULT false,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

**Notes:**
- In Phase 4, a `user_id` column is added; `is_default` becomes per-user.
- The `filters` JSONB shape mirrors the query parameters of `GET /api/v1/feed`.

---

## Phase 4 Migrations (Multi-User)

When Phase 4 begins, the following migrations are applied:

```sql
-- 1. Add user_id to per-user tables
ALTER TABLE feedback         ADD COLUMN user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE;
ALTER TABLE preferences      ADD COLUMN user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE;
ALTER TABLE filter_presets   ADD COLUMN user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE;

-- 2. Drop single-user unique indexes
DROP INDEX idx_feedback_content_type;
DROP INDEX ON preferences (key);

-- 3. Re-add with user_id scope
CREATE UNIQUE INDEX idx_feedback_user_content_type ON feedback(user_id, content_id, feedback_type);
CREATE UNIQUE INDEX idx_preferences_user_key        ON preferences(user_id, key);

-- 4. Enable Row-Level Security
ALTER TABLE feedback         ENABLE ROW LEVEL SECURITY;
ALTER TABLE preferences      ENABLE ROW LEVEL SECURITY;
ALTER TABLE filter_presets   ENABLE ROW LEVEL SECURITY;

-- 5. RLS policies (users see only their own rows)
CREATE POLICY feedback_user_policy ON feedback
  USING (user_id = auth.uid());

CREATE POLICY preferences_user_policy ON preferences
  USING (user_id = auth.uid());

CREATE POLICY filter_presets_user_policy ON filter_presets
  USING (user_id = auth.uid());
```

---

## Content Status State Machine

```
raw  ──► summarised  ──► ranked
 │              │
 │              └──► failed  (summarisation error)
 │
 └──────────────────► failed  (fetch error stored inline)
```

Only items with status `ranked` are returned by the feed API.

---

## Indexes Summary

| Table | Index | Type | Purpose |
|-------|-------|------|---------|
| sources | status, platform, category | BTREE | Filter by status/platform in admin UI |
| targets | source_id, status | BTREE | List targets per source |
| content | content_hash | UNIQUE BTREE | Deduplication |
| content | published_at DESC | BTREE | Default time sort |
| content | relevance_score DESC | BTREE | Ranking sort |
| content | status | BTREE | Pipeline processing queries |
| content | content_type | BTREE | Filter by type |
| content | fts | GIN | Full-text keyword search |
| feedback | content_id, feedback_type | UNIQUE BTREE | One signal per item per type |
| feedback | feedback_type, created_at | BTREE | Feedback history queries |
