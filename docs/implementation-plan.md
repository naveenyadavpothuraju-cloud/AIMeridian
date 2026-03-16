# Implementation Plan: AIMeridian

**Version:** 1.0
**Date:** 2026-03-12
**Status:** Phase 0 — Planning & Architecture
**Author:** Generated via planner agent

---

## Overview

AIMeridian is a personal AI developments tracker that aggregates content from arXiv, GitHub, Reddit, Hacker News, HuggingFace, Papers With Code, RSS blogs, X/Twitter, and LinkedIn into a single ranked, filterable feed. Content is fetched via public APIs and RSS feeds, then ranked and summarised by Claude LLMs. The user trains the feed over time using thumbs up/down feedback. The system is built with Next.js 15 (frontend, Vercel), FastAPI (backend, Railway), and PostgreSQL via Supabase.

---

## Milestone Summary Table

| Phase | Key Deliverable | Total Complexity | Exit Criteria |
|-------|----------------|-----------------|---------------|
| **Phase 0** | All architecture docs, ADRs, design system, prompts | ~3 days | All docs exist and are reviewed; all open decisions resolved |
| **Phase 1** | Working single-user feed with all sources, summaries, feedback, scheduler | ~3–4 weeks | Feed displays ranked content from all sources; feedback works; 80%+ test coverage |
| **Phase 2** | Source admin UI, full filter system, LLM ranker | ~2 weeks | Sources manageable via UI; all filter dimensions work; ranker produces scores |
| **Phase 3** | Smart ranking, UI polish, dark mode, bookmarks | ~1.5 weeks | Ranking uses multi-signal; dark/light mode; bookmarks; "more/less like this" |
| **Phase 4** | Multi-user auth, per-user feeds | ~1 week | Supabase Auth works; each user has independent feed, feedback, preferences |
| **Phase 5** | Rate limiting, caching, monitoring, security audit | ~1 week | All endpoints rate-limited; Redis cache; Sentry live; load test passes; security audit clean |

---

## Phase 0 — Planning & Architecture

### Open Architectural Decisions

These decisions MUST be resolved before any code is written. Each should produce an ADR in `docs/adr/`.

#### ADR-001: Component Library

**Decision needed:** shadcn/ui vs Radix UI vs Headless UI vs custom

| Option | Pros | Cons |
|--------|------|------|
| **shadcn/ui** (recommended) | Copy-paste ownership, Tailwind-native, excellent a11y via Radix primitives, large community | Must maintain copied code; updates are manual |
| Radix UI (bare) | Full control over styling, very accessible | More boilerplate, no pre-built styling |
| Headless UI | Simpler API | Fewer components, less ecosystem |

**Recommendation:** shadcn/ui. Aligns with Tailwind v4, gives full ownership of component code, covers all needed primitives (Card, Button, Badge, Dialog, Sheet, DropdownMenu, Tabs, Tooltip).

---

#### ADR-002: Background Job Runner

**Decision needed:** APScheduler vs Celery+Redis

| Option | Pros | Cons |
|--------|------|------|
| **APScheduler** (recommended for Phase 1–3) | Zero extra infra, runs in-process, simple cron config | Single-worker only; no distributed queue; no retry queue |
| Celery + Redis | Distributed, retries, monitoring (Flower), battle-tested | Requires Redis infra from day 1, operational complexity |

**Recommendation:** Start with APScheduler. Migrate to Celery+Redis in Phase 5 only if scheduler load demands it.

---

#### ADR-003: LLM Prompt Templates

**Summarisation prompt (claude-haiku-4-5):**
- Input: title, abstract/description, source, URL
- Output: 2–3 sentence summary focused on what is novel and why it matters
- Token budget: max 200 output tokens per item
- Timeout: 10 seconds per call
- Caching: keyed by SHA-256 hash of (title + abstract/description)

**Ranking prompt (claude-sonnet-4-6):**
- Input: batch of content items (max 50), user feedback history summary (top 20 upvoted themes, top 10 downvoted themes), source ratings
- Output: JSON array of `{content_id, relevance_score (0–100), reasoning (1 sentence)}`
- Token budget: max 4000 output tokens per batch
- Timeout: 60 seconds per call
- Caching: keyed by hash of (content_ids + feedback_version)

**Action:** Write full prompt templates in `docs/llm-prompts.md` with few-shot examples.

---

#### ADR-004: Content Refresh Cadence

**Recommendation:**
- Default: every 12 hours (6:00 UTC and 18:00 UTC)
- Configurable per-source override
- Environment variable `FETCH_CRON` controls global default
- Manual trigger always available via `POST /admin/trigger-fetch`

---

#### ADR-005: X.com and LinkedIn Data Strategy

**X.com options:**

| Approach | Feasibility | Risk |
|----------|------------|------|
| X API v2 Basic tier ($100/month) | 10,000 tweets/month read | Cost; rate limits |
| X API v2 Free tier | Write-only | Not usable |
| RSS bridge (RSSHub self-hosted) | Free | Fragile; may break |
| Manual curation | Zero cost | Not automated |

**Recommendation for X.com:** Use X API v2 Basic tier if budget allows. Otherwise defer and use RSSHub as best-effort fallback. Design fetcher interface so any approach can be swapped in.

**LinkedIn options:**

| Approach | Feasibility | Risk |
|----------|------------|------|
| LinkedIn API | Requires approved app, limited to own org | Cannot read arbitrary profiles |
| RSS via third-party | Unreliable | May break |
| Manual "Add Link" | Always works | Not automated |

**Recommendation for LinkedIn:** Defer automated fetching. Provide manual "Add Link" feature. Do not scrape.

---

### Phase 0 Tasks

| # | Task | Deliverable | Size | Dependencies | Agent/Skill | Exit Criteria |
|---|------|-------------|------|-------------|-------------|---------------|
| 0.1 | Write `docs/architecture.md` | System design with component diagram, data flow, deployment topology | M | None | `architect` agent | Doc covers all layers; reviewed |
| 0.2 | Write `docs/data-model.md` | Full DB schema: all tables, columns, types, constraints, indexes, RLS policies | M | None | `architect` agent + `postgres-patterns` | Schema covers all 6 tables |
| 0.3 | Write `docs/api-spec.md` | All FastAPI endpoints with Pydantic shapes, status codes, pagination | M | 0.2 | `api-design` skill | Every endpoint from CLAUDE.md specified |
| 0.4 | Write `docs/design-system.md` | Color palette, typography, spacing, component inventory, dark/light tokens | M | None | `frontend-patterns` skill | Design tokens defined; component list complete |
| 0.5 | Write `docs/llm-prompts.md` | Summarisation and ranking prompt templates with few-shot examples | M | None | `cost-aware-llm-pipeline` skill | Both prompts defined with token budgets and caching strategy |
| 0.6 | Resolve all open ADRs | ADR-001 through ADR-005 in `docs/adr/` | S | 0.1 | `architect` agent | All 5 ADRs have status "Accepted" |
| 0.7 | Document environment variables | Complete `.env.example` files for frontend and backend | S | 0.3 | None | All required variables listed with descriptions |
| 0.8 | Create `docs/source-catalog.md` | Initial list of all sources and targets to seed in Phase 1 | S | None | None | At least 20 sources across all categories listed |

---

## Phase 1 — Foundation (Single User, No Auth)

### Sub-phase 1a — Project Scaffolding

| # | Task | Deliverable | Size | Dependencies | Agent/Skill | Exit Criteria |
|---|------|-------------|------|-------------|-------------|---------------|
| 1a.1 | Initialize Next.js 15 app | `frontend/` with App Router, TypeScript strict, Tailwind v4, pnpm | M | Phase 0 | `frontend-patterns` skill | `pnpm dev` serves at localhost:3000; `pnpm type-check` passes |
| 1a.2 | Install shadcn/ui | Button, Card, Badge, Input, Sheet, Dialog, DropdownMenu, Tabs, Tooltip, Skeleton | M | 1a.1 | `frontend-patterns` skill | All components importable; render correctly |
| 1a.3 | Initialize FastAPI app | `backend/` with uv, pyproject.toml, app structure, health check endpoint | M | Phase 0 | `backend-patterns` skill | `GET /health` returns 200 |
| 1a.4 | Connect Supabase | Project created; connection string in `.env`; first empty migration runs | S | 1a.3 | `postgres-patterns` skill | `supabase db reset` succeeds; backend connects |
| 1a.5 | Configure linting and formatting | ESLint + Prettier (frontend), Ruff + mypy (backend), pre-commit hooks | S | 1a.1, 1a.3 | `coding-standards` skill | All linters pass with zero errors |
| 1a.6 | Set up GitHub Actions CI | Lint, type-check, test, build on every PR (both frontend and backend) | M | 1a.5 | `deployment-patterns` skill | PR triggers CI; all steps green |
| 1a.7 | Deploy skeleton frontend to Vercel | Blank Next.js app live at Vercel URL | S | 1a.1 | `deployment-patterns` skill | Public URL returns 200 |
| 1a.8 | Deploy skeleton backend to Railway | FastAPI health check live at Railway URL | S | 1a.3 | `deployment-patterns` skill | `/health` returns 200 |
| 1a.9 | Verify cross-service connectivity | Frontend can call backend health check | S | 1a.7, 1a.8 | None | Frontend fetches `/health` from backend and displays status |

### Sub-phase 1b — Database Schema & Core Models

| # | Task | Deliverable | Size | Dependencies | Agent/Skill | Exit Criteria |
|---|------|-------------|------|-------------|-------------|---------------|
| 1b.1 | Migration: `sources` table | id, name, platform, url, category, status, rating, created_at, updated_at | S | 1a.4 | `database-migrations` skill | Migration applies; table exists with correct columns |
| 1b.2 | Migration: `targets` table | id, source_id (FK), name, handle/query, type, status, created_at | S | 1b.1 | `database-migrations` skill | Migration applies; FK constraint enforced |
| 1b.3 | Migration: `content` table | id, source_id (FK), target_id (FK nullable), title, url, summary, content_hash, published_at, fetched_at, status, relevance_score, tags (JSONB) | M | 1b.1, 1b.2 | `database-migrations` skill | Indexes on content_hash, published_at, source_id |
| 1b.4 | Migration: `feedback` table | id, content_id (FK), feedback_type (up/down/save/skip), created_at | S | 1b.3 | `database-migrations` skill | Migration applies |
| 1b.5 | Migration: `preferences` table | id, key, value (JSONB), updated_at | S | 1a.4 | `database-migrations` skill | Migration applies |
| 1b.6 | Migration: `filter_presets` table | id, name, filters (JSONB), created_at | S | 1a.4 | `database-migrations` skill | Migration applies |
| 1b.7 | Write Pydantic models | Models for all 6 tables matching DB schema | M | 1b.1–1b.6 | `backend-patterns` skill | All models validate against sample data; unit tests pass |
| 1b.8 | Write SQLAlchemy models | ORM models with relationships | M | 1b.7 | `postgres-patterns` skill | All tables queryable; relationships load correctly |
| 1b.9 | Seed initial sources | Script to insert arXiv, GitHub, Reddit, HN, HF, PwC, RSS blogs | S | 1b.8, 0.8 | None | `SELECT count(*) FROM sources` >= 7 |

### Sub-phase 1c — First Fetcher (arXiv)

| # | Task | Deliverable | Size | Dependencies | Agent/Skill | Exit Criteria |
|---|------|-------------|------|-------------|-------------|---------------|
| 1c.1 | Define fetcher base interface | Abstract `BaseFetcher` with `fetch()` method signature | S | 1b.7 | `backend-patterns` skill | Interface defined with type hints |
| 1c.2 | Write arXiv fetcher tests | Unit tests with mocked HTTP responses | M | 1c.1 | `tdd-guide` agent | Tests written and FAILING (RED) |
| 1c.3 | Implement arXiv fetcher | `fetchers/arxiv.py` using arXiv public API | M | 1c.2 | `backend-patterns` skill | All unit tests PASS (GREEN); items stored in DB |
| 1c.4 | Write integration test | Test against live arXiv API (marked slow) | S | 1c.3 | `python-testing` skill | Integration test passes; at least 1 item fetched |

### Sub-phase 1d — Summariser

| # | Task | Deliverable | Size | Dependencies | Agent/Skill | Exit Criteria |
|---|------|-------------|------|-------------|-------------|---------------|
| 1d.1 | Write summariser tests | Unit tests mocking Claude API; test hash-based cache | M | 1b.7 | `tdd-guide` agent | Tests FAILING (RED) |
| 1d.2 | Implement summariser | `services/summariser.py` using claude-haiku-4-5; token budget, timeout, hash cache | M | 1d.1, 0.5 | `cost-aware-llm-pipeline` skill | Tests PASS (GREEN); same hash never re-summarised |
| 1d.3 | Integrate into fetch pipeline | After fetch, summariser processes items with status `raw` | S | 1d.2, 1c.3 | `backend-patterns` skill | After fetch, items have non-null summary |

### Sub-phase 1e — Basic Feed UI

| # | Task | Deliverable | Size | Dependencies | Agent/Skill | Exit Criteria |
|---|------|-------------|------|-------------|-------------|---------------|
| 1e.1 | Create shared TypeScript types | Types for ContentItem, Source, Feedback matching backend models | S | 1b.7 | `frontend-patterns` skill | Types in `frontend/types/` |
| 1e.2 | Create API client module | `frontend/lib/api.ts` typed fetch wrappers for all endpoints | M | 1e.1 | `frontend-patterns` skill | Client covers `/feed`, `/sources`, `/feedback` |
| 1e.3 | Build FeedCard component | Title, source badge, date, summary, link, thumbs up/down | M | 1a.2, 1e.1 | `frontend-patterns` skill | Renders with mock data; responsive at 390px and 1440px |
| 1e.4 | Build FeedList component | Scrollable list; single column mobile, two columns desktop | M | 1e.3 | `frontend-patterns` skill | Responsive layout verified |
| 1e.5 | Build feed page | `app/(feed)/page.tsx` fetching from backend, rendering FeedList | M | 1e.4, 1e.2 | `frontend-patterns` skill | Page loads and displays content items |
| 1e.6 | Add loading skeleton | Skeleton cards during fetch; no layout shift | S | 1e.3 | `frontend-patterns` skill | Skeleton visible during fetch |
| 1e.7 | Add empty state | Friendly message when feed is empty | S | 1e.5 | `frontend-patterns` skill | Empty state renders |
| 1e.8 | Write E2E test | Playwright: page loads, cards render, links work | M | 1e.5 | `e2e-runner` agent | E2E test passes |

### Sub-phase 1f — Feedback System

| # | Task | Deliverable | Size | Dependencies | Agent/Skill | Exit Criteria |
|---|------|-------------|------|-------------|-------------|---------------|
| 1f.1 | Build feedback API endpoint | `POST /api/v1/feedback` with content_id and feedback_type | S | 1b.4, 1b.8 | `api-design` skill | Endpoint stores feedback; returns 201 |
| 1f.2 | Write feedback API tests | Unit tests: create, duplicate handling, validation | S | 1f.1 | `tdd-guide` agent | Tests pass |
| 1f.3 | Wire thumbs up/down in FeedCard | Optimistic UI update; toggle state; call feedback API | M | 1f.1, 1e.3 | `frontend-patterns` skill | Click thumb → immediate visual change → persisted in DB |
| 1f.4 | Basic re-ranking by feedback | Feed sorts by relevance_score with upvoted items boosted | M | 1f.1 | `backend-patterns` skill | Upvoting item causes it to rank higher on next feed fetch |
| 1f.5 | Write E2E test | Playwright: thumbs up, verify state persists on reload | S | 1f.3 | `e2e-runner` agent | E2E test passes |

### Sub-phase 1g — Remaining Fetchers

Each fetcher: (1) write tests → (2) implement → (3) integration test.

| # | Fetcher | Source | Size | Exit Criteria |
|---|---------|--------|------|---------------|
| 1g.1 | GitHub | GitHub REST API — trending repos, org repos, topic search | M | Tests pass; items in DB |
| 1g.2 | Reddit | Reddit JSON API (no auth) — configured subreddits | M | Tests pass; posts in DB |
| 1g.3 | Hacker News | Algolia HN Search API — AI-related stories | M | Tests pass; HN items in DB |
| 1g.4 | RSS feeds | `feedparser` — generic RSS/Atom for blogs and newsletters | M | Tests pass; blog posts in DB |
| 1g.5 | HuggingFace | HF API — new model releases, trending models | M | Tests pass; HF items in DB |
| 1g.6 | Papers With Code | PwC API — SOTA results and linked papers | M | Tests pass; PwC items in DB |
| 1g.7 | X.com (conditional) | X API v2 Basic OR stub per ADR-005 | M | If API: tests pass, tweets in DB. If deferred: stub returns empty with TODO |
| 1g.8 | LinkedIn (manual) | `POST /api/v1/content/manual` for manually added items | S | Endpoint stores item; returns 201 |

All 1g tasks use: `tdd-guide` agent + `backend-patterns` skill

### Sub-phase 1h — Scheduler

| # | Task | Deliverable | Size | Dependencies | Agent/Skill | Exit Criteria |
|---|------|-------------|------|-------------|-------------|---------------|
| 1h.1 | Write scheduler tests | Unit tests for cron parsing, fetcher orchestration | M | 1g.1–1g.8 | `tdd-guide` agent | Tests FAILING (RED) |
| 1h.2 | Implement APScheduler | `scheduler/jobs.py` — runs all active fetchers → summariser on `FETCH_CRON` | M | 1h.1 | `autonomous-loops` skill | Tests PASS; scheduler starts with app; runs at configured time |
| 1h.3 | Manual trigger endpoint | `POST /admin/trigger-fetch` → 202 Accepted | S | 1h.2 | `api-design` skill | Endpoint triggers fetch cycle |
| 1h.4 | Logging and error handling | Each fetcher logs start/end/error; one failure does not crash others | S | 1h.2 | `backend-patterns` skill | Logs show execution; partial failure handled gracefully |

---

## Phase 2 — Source Management & Filtering

### Sub-phase 2a — Sources Admin UI

| # | Task | Deliverable | Size | Dependencies | Agent/Skill | Exit Criteria |
|---|------|-------------|------|-------------|-------------|---------------|
| 2a.1 | Build Sources CRUD API | Full CRUD for sources and nested targets | M | 1b.8 | `api-design` skill + `tdd-guide` agent | All operations work; tests pass |
| 2a.2 | Build SourceList page | `app/sources/page.tsx` — table with status badges, rating stars, actions | L | 2a.1, 1a.2 | `frontend-patterns` skill | Page renders; status toggles work |
| 2a.3 | Build SourceDetail/Edit page | `app/sources/[id]/page.tsx` — edit source, manage targets, set rating | M | 2a.1, 2a.2 | `frontend-patterns` skill | All fields editable; targets manageable |
| 2a.4 | Build AddSource dialog | Dialog with validation to add new source | M | 2a.1 | `frontend-patterns` skill | New source created via UI; appears in list |
| 2a.5 | Implement trial mode | New sources shown in "New Sources" section; graduates to main feed after rating | M | 2a.1, 1e.5 | `backend-patterns` skill | Trial content in separate section |
| 2a.6 | 5-star rating UI | Star rating component; rating updates DB; affects ranking weight | M | 2a.2 | `frontend-patterns` skill | Rating persists; sources rated ≤2 auto-paused |
| 2a.7 | E2E tests | Playwright: add, edit, archive, rate source | M | 2a.2–2a.6 | `e2e-runner` agent | All E2E tests pass |

### Sub-phase 2b — Full Filter System

| # | Task | Deliverable | Size | Dependencies | Agent/Skill | Exit Criteria |
|---|------|-------------|------|-------------|-------------|---------------|
| 2b.1 | Feed API filter params | `/feed` accepts: type, topic, source_id, date_from, date_to, status, rating_min, search_query | M | 1e.5 | `api-design` skill + `tdd-guide` agent | Filters compose (AND logic); all dimensions tested |
| 2b.2 | FilterBar component | Horizontal bar with active filter chips (dismissible with ×) | M | 1a.2 | `frontend-patterns` skill | Dismissing chip removes filter and refreshes feed |
| 2b.3 | FilterPanel component | Checkboxes, topic tags, source picker, date range, read status — all 7 dimensions | L | 2b.2 | `frontend-patterns` skill | All filter dimensions available |
| 2b.4 | Mobile bottom sheet | FilterPanel as bottom sheet on mobile (< 768px) | M | 2b.3 | `frontend-patterns` skill | Sheet on mobile; panel on desktop |
| 2b.5 | Keyword search | Free-text search on title + summary; debounced; `tsvector` or ILIKE | M | 2b.1 | `frontend-patterns` skill + `postgres-patterns` skill | Search returns relevant results |
| 2b.6 | Filter presets | Save/load/delete named presets; API + UI | M | 1b.6, 2b.3 | `api-design` skill + `frontend-patterns` skill | Save, load, delete presets all work |
| 2b.7 | E2E tests | Playwright: apply filter, verify feed, save preset, load preset | M | 2b.2–2b.6 | `e2e-runner` agent | All E2E tests pass |

### Sub-phase 2c — LLM Ranker

| # | Task | Deliverable | Size | Dependencies | Agent/Skill | Exit Criteria |
|---|------|-------------|------|-------------|-------------|---------------|
| 2c.1 | Write ranker tests | Unit tests mocking Claude API; batch processing, feedback integration | M | 1b.7 | `tdd-guide` agent | Tests FAILING (RED) |
| 2c.2 | Implement ranker | `services/ranker.py` using claude-sonnet-4-6; batches 50 items; feedback summary in prompt | L | 2c.1, 0.5 | `cost-aware-llm-pipeline` skill | Tests PASS; items get relevance_score 0–100 |
| 2c.3 | Integrate ranker into pipeline | Ranker runs after summariser; scores stored in `content.relevance_score` | S | 2c.2, 1h.2 | `backend-patterns` skill | After fetch cycle, all items have updated scores |
| 2c.4 | Feed sorts by relevance_score | Default sort uses LLM score weighted by source rating | S | 2c.3 | None | Highest-scored items appear first |

---

## Phase 3 — Personalisation & UI Polish

### Sub-phase 3a — Smarter Ranking

| # | Task | Deliverable | Size | Dependencies | Agent/Skill | Exit Criteria |
|---|------|-------------|------|-------------|-------------|---------------|
| 3a.1 | Multi-signal ranking | Ranker incorporates: thumbs up rate, skip rate, save rate, source rating | M | 2c.2 | `cost-aware-llm-pipeline` skill | All signal types in prompt; scores reflect behavior |
| 3a.2 | "More/Less like this" | Buttons on FeedCard; stores preference signal; feeds into next ranking cycle | M | 3a.1 | `frontend-patterns` skill + `api-design` skill | Signal stored; next ranking reflects it |
| 3a.3 | Discovery assistant | Suggests new targets based on upvoted content patterns | L | 3a.1 | `cost-aware-llm-pipeline` skill | Suggestions appear in Sources UI |

### Sub-phase 3b — UI Polish

| # | Task | Deliverable | Size | Dependencies | Agent/Skill | Exit Criteria |
|---|------|-------------|------|-------------|-------------|---------------|
| 3b.1 | Dark / light mode | Theme toggle; persisted in preferences; Tailwind `dark:` variant; no FOUC | M | 1a.1 | `frontend-patterns` skill | Toggle works; preference persists |
| 3b.2 | Bookmarks / saved items | Save button on card; `/saved` page listing bookmarked items | M | 1f.1 | `frontend-patterns` skill | Save persists; saved page renders correctly |
| 3b.3 | "Since last visit" badge | Track `last_visit` in preferences; badge on newer items | S | 1b.5 | `frontend-patterns` skill | Badge shows on new items; clears after view |
| 3b.4 | Keyword notifications | Configurable keywords highlighted in feed when matched | M | 2b.5 | `frontend-patterns` skill | Matching items distinguished visually; configurable in settings |
| 3b.5 | Settings page | `app/settings/page.tsx` — refresh cadence, keywords, theme, default filters | M | 1b.5 | `frontend-patterns` skill | All preferences editable and persisted |
| 3b.6 | Layout and navigation polish | Header, nav, breadcrumbs, page transitions | M | 1e.5 | `frontend-patterns` skill | Navigation intuitive on mobile and desktop |

---

## Phase 4 — Multi-User

### Sub-phase 4a — Authentication

| # | Task | Deliverable | Size | Dependencies | Agent/Skill | Exit Criteria |
|---|------|-------------|------|-------------|-------------|---------------|
| 4a.1 | Enable Supabase Auth | Email + Google OAuth configured in Supabase dashboard | S | None | `security-review` skill | Auth providers active |
| 4a.2 | Add user_id FK to tables | Migration: `user_id` on feedback, preferences, filter_presets; RLS policies | M | 4a.1 | `database-migrations` skill + `security-review` skill | RLS enforced; users only read/write their own rows |
| 4a.3 | Auth middleware (Next.js) | Protected routes redirect to login; session via Supabase Auth helpers | M | 4a.1 | `frontend-patterns` skill + `security-review` skill | Unauthenticated users redirected |
| 4a.4 | Auth middleware (FastAPI) | JWT validation; extract user_id from token on all protected endpoints | M | 4a.1 | `backend-patterns` skill + `security-review` skill | Invalid tokens → 401 |
| 4a.5 | Login / signup pages | `app/login/` and `app/signup/` with email + Google OAuth | M | 4a.1 | `frontend-patterns` skill | Sign up and log in work; session persists |
| 4a.6 | E2E auth flow tests | Playwright: sign up, log in, access protected page, log out | M | 4a.5 | `e2e-runner` agent | All auth E2E tests pass |

### Sub-phase 4b — Per-User Personalisation

| # | Task | Deliverable | Size | Dependencies | Agent/Skill | Exit Criteria |
|---|------|-------------|------|-------------|-------------|---------------|
| 4b.1 | Per-user sources and targets | Each user has own source list; global defaults inherited by new users | L | 4a.2 | `backend-patterns` skill | Two users see different source lists |
| 4b.2 | Per-user feed ranking | Ranker uses per-user feedback; feeds are fully personalised | M | 4a.2, 2c.2 | `cost-aware-llm-pipeline` skill | Two users with different feedback see different rankings |
| 4b.3 | Admin user role | Admin can manage global source suggestions; protected endpoints | M | 4a.2 | `security-review` skill | Non-admins cannot access admin endpoints |

---

## Phase 5 — Production Hardening

| # | Task | Deliverable | Size | Dependencies | Agent/Skill | Exit Criteria |
|---|------|-------------|------|-------------|-------------|---------------|
| 5.1 | Rate limiting | FastAPI middleware: per-IP and per-user limits on all endpoints | M | 4a.4 | `security-review` skill | 429 returned when limit exceeded |
| 5.2 | Redis caching layer | Cache ranked feed in Redis; invalidate on new fetch or feedback; configurable TTL | M | None | `backend-patterns` skill | Feed serves from cache; miss triggers DB query |
| 5.3 | Sentry integration | Error monitoring for frontend (Next.js) and backend (FastAPI) | M | None | `deployment-patterns` skill | Errors in Sentry; source maps uploaded |
| 5.4 | Uptime monitoring | External pings on health endpoints; alerts on downtime | S | 1a.7, 1a.8 | `deployment-patterns` skill | Alert fires within 5 minutes of downtime |
| 5.5 | Load testing | k6 or Locust against staging; identify bottlenecks | M | 5.2 | None | Feed handles 100 concurrent users; p95 < 500ms |
| 5.6 | Security audit | `security-reviewer` agent full audit; fix all critical/high findings | L | All phases | `security-reviewer` agent | Zero critical/high findings; report documented |
| 5.7 | GDPR compliance | Cookie consent, data deletion endpoint, privacy policy page | M | 4a.1 | `security-review` skill | Users can request data deletion; privacy policy exists |
| 5.8 | Evaluate Celery migration | Migrate APScheduler → Celery+Redis if scheduler load warrants it | L | 5.2 | `architect` agent | Decision in ADR; migrated if justified |

---

## Dependency Graph

```
Phase 0 (all docs + ADRs resolved)
   │
   ├──► Phase 1a (scaffolding)
   │        │
   │        ├──► Phase 1b (DB schema + models)
   │        │        │
   │        │        ├──► Phase 1c (arXiv fetcher)
   │        │        │        │
   │        │        │        └──► Phase 1d (summariser)
   │        │        │                    │
   │        │        │        ┌───────────┘
   │        │        │        ▼
   │        │        ├──► Phase 1e (feed UI) ──────────────┐
   │        │        │                                     │
   │        │        │        ┌────────────────────────────┘
   │        │        │        ▼
   │        │        ├──► Phase 1f (feedback)
   │        │        │        │
   │        │        ├──► Phase 1g (remaining fetchers)
   │        │        │        │
   │        │        └──► Phase 1h (scheduler) ◄────────────┘
   │        │
   │        ├──► Phase 2a (sources admin UI)
   │        ├──► Phase 2b (filters)
   │        └──► Phase 2c (LLM ranker) ◄── Phase 2b
   │
   ├──► Phase 3a (smart ranking) ◄── Phase 2c
   │        └──► Phase 3a.3 (discovery assistant)
   │
   ├──► Phase 3b (UI polish) ◄── Phase 1e, 1f
   │
   ├──► Phase 4a (auth) ◄── Phase 1 complete
   │        └──► Phase 4b (per-user) ◄── Phase 2c, 4a
   │
   └──► Phase 5 (hardening) ◄── Phase 4 complete

Parallel opportunities:
  - 1c (arXiv fetcher) and 1e (feed UI) start in parallel after 1b
  - 1g (remaining fetchers) and 1e/1f (UI) proceed in parallel
  - 2a (sources UI) and 2c (ranker) start in parallel after 1b
  - 3a (smart ranking) and 3b (UI polish) proceed in parallel
  - 5.1–5.4 (rate limit, cache, sentry, uptime) all proceed in parallel
```

---

## Risk Register

| # | Risk | Likelihood | Impact | Mitigation |
|---|------|-----------|--------|------------|
| R1 | X.com API expensive or unavailable | High | Medium | Defer; use RSSHub as fallback; swappable fetcher interface (ADR-005) |
| R2 | LinkedIn has no viable automated source | High | Low | Manual "Add Link" feature; revisit periodically; do not scrape |
| R3 | LLM costs escalate with content volume | Medium | High | Use haiku for summarisation; batch ranking (50 items/call); cache by content hash; daily token budget with hard cutoff |
| R4 | arXiv/Reddit/HN API rate limits hit | Medium | Medium | Exponential backoff; stagger fetchers; cache responses; reduce fetch frequency if needed |
| R5 | APScheduler single-worker bottleneck | Low (Ph 1–3) | Medium | Monitor job duration; migrate to Celery+Redis in Phase 5 if jobs exceed 10 minutes |
| R6 | Supabase free tier limits | Medium | Medium | Monitor row counts and API calls; upgrade to Pro ($25/month) before hitting limits |
| R7 | Content deduplication failures | Medium | Low | content_hash (SHA-256 of title+url) as unique constraint; upsert on conflict; log duplicates |
| R8 | Prompt quality degrades ranking accuracy | Medium | High | A/B test prompts manually in Phase 2c; version prompts in `docs/llm-prompts.md`; track via feedback correlation |
| R9 | Railway cold starts slow API | Low | Medium | Use Railway always-on option; health check pings; frontend shows skeleton gracefully |
| R10 | Scope creep delays launch | High | High | Strictly enforce phase gates; Phase 1 is the MVP; do not add Phase 2+ features early |
| R11 | RLS misconfiguration leaks data in Phase 4 | Low | Critical | Security audit before Phase 4 launch; write RLS integration tests; `security-reviewer` agent on all migrations |
| R12 | Frontend bundle size grows too large | Low | Medium | Dynamic imports for filter panel and source admin; monitor with `@next/bundle-analyzer` |

---

## Testing Strategy

| Layer | Tool | Coverage Target | What to Test |
|-------|------|----------------|-------------|
| Python unit | pytest + pytest-mock | 80%+ | Fetchers (mocked HTTP), summariser (mocked Claude), ranker (mocked Claude), all API endpoints |
| Python integration | pytest + httpx (TestClient) | Key flows | Full fetch → summarise → rank pipeline; API endpoint integration |
| Frontend unit | Vitest + React Testing Library | 80%+ | Component rendering; API client error handling; filter logic |
| Frontend E2E | Playwright | Critical paths | Feed loads, feedback works, filters work, source management, auth flow |
| Load tests | k6 or Locust (Phase 5) | p95 < 500ms | Feed endpoint under 100 concurrent users |
| Security | `security-reviewer` agent | Zero critical | Auth bypass, SQL injection, XSS, CSRF, secret leakage |

---

## Notes

- **No code is written in this document.** This is a planning artifact only.
- **Each sub-phase is independently deployable.** The feed works after Phase 1e even without all fetchers.
- **TDD is mandatory for all backend services.** RED → GREEN → IMPROVE.
- **`code-reviewer` agent runs after every meaningful code change.** No exceptions.
- **`security-reviewer` agent runs at the end of every phase.** No exceptions.
- **CLAUDE.md must be updated** whenever the active phase changes.
