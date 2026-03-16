# Architecture — AIMeridian

**Version:** 1.0
**Phase:** 0 — Planning
**Last Updated:** 2026-03-12

---

## System Overview

AIMeridian is a personal AI developments tracker. It continuously pulls content from public APIs and RSS feeds, uses LLMs only for ranking and summarisation, and presents the result as a ranked, filterable, personalisable feed. The user trains the feed over time via thumbs up/down feedback.

---

## Component Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        USER (Browser / Mobile)                      │
└───────────────────────────────┬─────────────────────────────────────┘
                                │ HTTPS
┌───────────────────────────────▼─────────────────────────────────────┐
│                  Next.js 15 Frontend (Vercel)                       │
│                                                                     │
│  ┌────────────┐  ┌──────────────┐  ┌─────────────┐  ┌───────────┐  │
│  │  Feed UI   │  │  Filter Bar  │  │ Source Admin│  │ Settings  │  │
│  │  (cards,   │  │  + Panel     │  │ (CRUD, rate)│  │ (prefs,   │  │
│  │  feedback) │  │              │  │             │  │  presets) │  │
│  └────────────┘  └──────────────┘  └─────────────┘  └───────────┘  │
│                                                                     │
│  lib/api.ts  ──  typed fetch wrappers to FastAPI backend            │
└───────────────────────────────┬─────────────────────────────────────┘
                                │ REST API (JSON) over HTTPS
┌───────────────────────────────▼─────────────────────────────────────┐
│                  Python FastAPI Backend (Railway)                   │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  API Layer  (/api/v1/)                                       │   │
│  │  feed · sources · targets · feedback · filter-presets ·      │   │
│  │  preferences · admin/trigger-fetch                           │   │
│  └──────────────────────────┬───────────────────────────────────┘   │
│                             │                                       │
│  ┌──────────────────────────▼───────────────────────────────────┐   │
│  │  Service Layer                                               │   │
│  │                                                              │   │
│  │  ┌─────────────────┐  ┌──────────────┐  ┌───────────────┐   │   │
│  │  │   Fetchers      │  │  Summariser  │  │    Ranker     │   │   │
│  │  │  (one per       │  │  claude-     │  │  claude-      │   │   │
│  │  │   source type)  │  │  haiku-4-5   │  │  sonnet-4-6   │   │   │
│  │  │                 │  │  + hash      │  │  + feedback   │   │   │
│  │  │  arXiv          │  │  cache       │  │  context      │   │   │
│  │  │  GitHub         │  └──────────────┘  └───────────────┘   │   │
│  │  │  Reddit                                                   │   │
│  │  │  Hacker News    │                                         │   │
│  │  │  HuggingFace    │                                         │   │
│  │  │  Papers w/ Code │                                         │   │
│  │  │  RSS / Atom     │                                         │   │
│  │  │  X.com (opt.)   │                                         │   │
│  │  └─────────────────┘                                         │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  Scheduler (APScheduler)                                     │   │
│  │  Cron: FETCH_CRON (default: 0 6,18 * * *)                    │   │
│  │  Flow: fetch → summarise → rank → store scores               │   │
│  └──────────────────────────────────────────────────────────────┘   │
└───────────────────────────────┬─────────────────────────────────────┘
                                │ SQL (SQLAlchemy / Supabase client)
┌───────────────────────────────▼─────────────────────────────────────┐
│                  PostgreSQL via Supabase                            │
│                                                                     │
│   sources · targets · content · feedback · preferences ·           │
│   filter_presets                                                    │
│                                                                     │
│   Row-Level Security (RLS) enforced in Phase 4+                    │
└─────────────────────────────────────────────────────────────────────┘

External APIs (outbound only — never inbound):
  arXiv API · GitHub REST API · Reddit JSON API · Algolia HN API
  HuggingFace API · Papers With Code API · feedparser (RSS/Atom)
  X API v2 (optional) · Anthropic Claude API
```

---

## Data Flow

### Scheduled Fetch Cycle (runs every 12 hours by default)

```
1. Scheduler fires (APScheduler cron)
      │
2. For each ACTIVE source:
      │
      ├─► Fetcher pulls items from public API / RSS feed
      │   - Deduplicates by content_hash (SHA-256 of title + url)
      │   - Stores new items in `content` table with status = 'raw'
      │
3. Summariser processes all items with status = 'raw'
      │   - Calls claude-haiku-4-5 with title + abstract
      │   - Skips items where content_hash already has a cached summary
      │   - Stores summary; sets status = 'summarised'
      │
4. Ranker processes all items with status = 'summarised'
      │   - Batches 50 items per call to claude-sonnet-4-6
      │   - Sends user feedback history summary as context
      │   - Stores relevance_score (0–100) on each item
      │   - Sets status = 'ranked'
      │
5. Frontend reads items with status = 'ranked'
      - Sorted by relevance_score DESC, then published_at DESC
      - Filtered by user-selected filter dimensions
```

### User Interaction Flow

```
User views feed
      │
      ├─► Thumbs up / down / save / skip
      │         └─► POST /api/v1/feedback
      │               └─► Stored in `feedback` table
      │                     └─► Influences next ranking cycle
      │
      ├─► Applies filters (type, topic, source, date, search)
      │         └─► GET /api/v1/feed?type=paper&source_id=1&...
      │
      └─► Saves filter preset
                └─► POST /api/v1/filter-presets
```

---

## Deployment Topology

```
GitHub Repository
      │
      ├─► Vercel (auto-deploy on push to main)
      │     - Next.js 15 frontend
      │     - Preview deployments on PRs
      │     - Environment: NEXT_PUBLIC_SUPABASE_URL, BACKEND_API_URL
      │
      ├─► Railway (auto-deploy on push to main)
      │     - FastAPI backend (uvicorn)
      │     - APScheduler runs in-process
      │     - Environment: DATABASE_URL, ANTHROPIC_API_KEY, FETCH_CRON
      │
      └─► Supabase (managed PostgreSQL)
            - Hosted PostgreSQL
            - Built-in auth (Phase 4)
            - Row-Level Security policies
            - Migrations via Alembic (applied from Railway)
```

---

## Component Boundaries

### Frontend Responsibilities
- Render and paginate the content feed
- Manage filter state (client-side URL params)
- Send feedback to backend API (optimistic UI update)
- Manage user preferences (dark mode, default filters, keywords)
- Source and target management UI (CRUD)
- **Does NOT** talk directly to Supabase (all reads/writes go via FastAPI)
- **Does NOT** call Claude API

### Backend Responsibilities
- All data fetching from external sources (APIs, RSS)
- Deduplication, summarisation, and ranking
- Serving the ranked, filtered feed
- Storing feedback and preferences
- Scheduling and orchestrating the fetch pipeline
- **Does NOT** serve static assets
- **Does NOT** do server-side rendering

### Supabase Responsibilities
- Persistent storage for all data
- Auth provider (Phase 4)
- Row-Level Security enforcement (Phase 4)
- **Does NOT** contain business logic

---

## Key Architectural Decisions

| Decision | Choice | Rationale | ADR |
|----------|--------|-----------|-----|
| Component library | shadcn/ui | Tailwind-native, Radix a11y, copy-paste ownership | ADR-001 |
| Background jobs | APScheduler (Phase 1–3) | Zero infra, in-process, simple cron | ADR-002 |
| LLM usage | Summarise + rank only | Fetching via APIs is cheaper, faster, more reliable | ADR-003 |
| Summarisation model | claude-haiku-4-5 | High volume, cost-sensitive | ADR-003 |
| Ranking model | claude-sonnet-4-6 | Needs reasoning; lower volume | ADR-003 |
| Refresh cadence | Every 12 hours | Balance between freshness and API rate limits | ADR-004 |
| X.com strategy | X API v2 Basic (if budget) or RSSHub fallback | No free read access available | ADR-005 |
| LinkedIn strategy | Manual "Add Link" | No viable automated read API | ADR-005 |

---

## Non-Functional Requirements

| Requirement | Target |
|-------------|--------|
| Feed page load (p95) | < 1 second (served from DB cache in Phase 5) |
| Feedback API response | < 200ms (simple DB write) |
| Scheduler job duration | < 10 minutes per full cycle |
| LLM summarisation | < 10 seconds per item (timeout enforced) |
| LLM ranking batch | < 60 seconds per 50-item batch (timeout enforced) |
| Mobile support | Works at 390px width; bottom sheet for filters |
| Uptime | 99%+ (monitored with external pings) |
| Test coverage | 80%+ on all backend services and frontend components |

---

## Security Boundaries

- Anthropic API key: backend `.env` only — never in frontend
- Supabase service role key: backend `.env` only — never in frontend
- Frontend uses Supabase anon key (public) — safe for browser
- All user input validated via Pydantic (backend) before DB writes
- Rate limiting on all API endpoints (Phase 5)
- RLS policies enforce per-user data isolation (Phase 4)
