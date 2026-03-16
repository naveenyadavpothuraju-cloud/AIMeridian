# CLAUDE.md — AI Developments Tracker

This file is the single source of truth for Claude when working on this project.
Read it fully before touching any code. Follow every instruction exactly.

---

## Project Overview

**AIMeridian** — A personal website that aggregates AI developments from across the internet into a
single, ranked, filterable feed. Content is fetched via public APIs and RSS feeds,
then ranked and summarised by an LLM. The user trains the feed over time using a
thumbs up / thumbs down feedback system.

**Current Phase:** Phase 1b — Database Schema & Core Models
> Update this line every time the active phase changes.

---

## Confirmed Tech Stack

| Layer | Technology | Notes |
|---|---|---|
| **Frontend** | Next.js 15 (App Router) + TypeScript | Strict mode enabled |
| **Styling** | Tailwind CSS v4 | Mobile-first, utility-first |
| **Backend** | Python + FastAPI | Data pipelines, LLM ranking, RSS/API fetching |
| **Database** | PostgreSQL via Supabase | Managed, built-in auth for Phase 3 |
| **Frontend Hosting** | Vercel | Auto-deploy from GitHub, preview deployments |
| **Backend Hosting** | Railway | FastAPI service (Vercel does not support long-running Python) |
| **Package Manager (JS)** | pnpm | Use pnpm only. Never npm or yarn. |
| **Package Manager (Py)** | uv | Faster than pip. Use uv for all Python deps. |
| **LLM Usage** | Anthropic Claude API | Only for ranking and summarisation. Never for data fetching. |

---

## Repository Structure

```
AI-DEVELOPMENTS-TRACKER/
├── website/                  ← working directory for this project
│   ├── CLAUDE.md             ← this file
│   ├── frontend/             ← Next.js app
│   │   ├── app/              ← App Router pages and layouts
│   │   │   ├── (feed)/       ← Main feed route group
│   │   │   ├── sources/      ← Source management UI
│   │   │   ├── settings/     ← User preferences
│   │   │   └── api/          ← Next.js API routes (lightweight BFF only)
│   │   ├── components/       ← Reusable UI components
│   │   │   ├── feed/         ← Feed-specific components
│   │   │   ├── filters/      ← Filter bar, filter panel, filter chips
│   │   │   ├── sources/      ← Source and target management UI
│   │   │   └── ui/           ← Generic primitives (Button, Card, Badge, etc.)
│   │   ├── lib/              ← Frontend utilities, hooks, API clients
│   │   ├── types/            ← Shared TypeScript types
│   │   ├── public/
│   │   ├── package.json
│   │   ├── tailwind.config.ts
│   │   └── tsconfig.json
│   ├── backend/              ← Python FastAPI service
│   │   ├── app/
│   │   │   ├── main.py       ← FastAPI entry point
│   │   │   ├── api/          ← Route handlers
│   │   │   ├── services/     ← Business logic (fetchers, ranker, summariser)
│   │   │   │   ├── fetchers/ ← One fetcher per source type (arxiv, github, reddit…)
│   │   │   │   ├── ranker.py ← LLM-based content ranking
│   │   │   │   └── summariser.py ← LLM-based summarisation
│   │   │   ├── models/       ← SQLAlchemy / Pydantic models
│   │   │   ├── db/           ← Database connection, migrations (Alembic)
│   │   │   └── scheduler/    ← Background jobs (APScheduler or Celery)
│   │   ├── tests/
│   │   ├── pyproject.toml
│   │   └── .env.example
│   ├── supabase/             ← Supabase config and SQL migrations
│   │   └── migrations/
│   └── docs/                 ← Architecture diagrams, ADRs, planning docs
│       ├── architecture.md
│       ├── data-model.md
│       ├── api-spec.md
│       └── adr/              ← Architecture Decision Records
```

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        USER (Browser/Mobile)                │
└───────────────────────┬─────────────────────────────────────┘
                        │ HTTPS
┌───────────────────────▼─────────────────────────────────────┐
│              Next.js Frontend (Vercel)                      │
│  Feed UI · Filters · Source Admin · Settings                │
│  Calls FastAPI backend for all data                         │
└───────────────────────┬─────────────────────────────────────┘
                        │ REST API
┌───────────────────────▼─────────────────────────────────────┐
│              Python FastAPI Backend (Railway)               │
│                                                             │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │  Fetchers   │  │   Ranker     │  │   Summariser     │   │
│  │ (RSS/APIs)  │  │ (Claude API) │  │  (Claude API)    │   │
│  └──────┬──────┘  └──────┬───────┘  └────────┬─────────┘   │
│         │                │                   │             │
│  ┌──────▼────────────────▼───────────────────▼─────────┐   │
│  │              Scheduler (runs daily/configurable)     │   │
│  └──────────────────────────────────────────────────────┘   │
└───────────────────────┬─────────────────────────────────────┘
                        │ SQL
┌───────────────────────▼─────────────────────────────────────┐
│              PostgreSQL via Supabase                        │
│  content · sources · targets · feedback · preferences       │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow
1. **Scheduler** triggers fetchers on a configured cadence (default: daily)
2. **Fetchers** pull from public APIs (arXiv, GitHub, Reddit) and RSS feeds
3. Raw items are stored in `content` table with status `raw`
4. **Summariser** generates a short summary for each item via Claude API
5. **Ranker** scores each item using user feedback history + Claude API
6. Frontend reads ranked, summarised items from Supabase
7. User interacts (thumbs up/down, save, skip) → feedback stored → influences next ranking cycle

### LLM Usage Rules (CRITICAL)
- **LLM is NEVER used for data fetching** — only APIs and RSS feeds fetch data
- **LLM is used ONLY for:** ranking content by relevance, generating summaries
- Always use `claude-haiku-4-5` for summarisation (high volume, cost-sensitive)
- Always use `claude-sonnet-4-6` for ranking (needs reasoning, lower volume)
- Every LLM call must have a **token budget** and **timeout**
- Cache LLM outputs using content hash — never re-summarise the same content twice

---

## Development Philosophy

> **Plan first. Always. No exceptions.**

1. Never write code before reading the relevant section of this file
2. Never implement a feature without first checking the phased roadmap below
3. Always write tests before writing implementation (TDD)
4. Always run code review agent after writing meaningful code
5. Always verify 80%+ test coverage before marking a sub-phase complete
6. Commit often with conventional commit messages
7. Never jump ahead to a later phase without completing and verifying the current one

---

## Phased Roadmap

### Phase 0 — Planning & Architecture ← CURRENT PHASE
**Goal:** All decisions made on paper before a single line of product code is written.

- [x] Finalise project name — **AIMeridian**
- [x] Write `docs/architecture.md`
- [x] Write `docs/data-model.md`
- [x] Write `docs/api-spec.md`
- [x] Write `docs/design-system.md`
- [x] Write `docs/llm-prompts.md`
- [x] Write `docs/source-catalog.md`
- [x] Write `docs/implementation-plan.md`
- [x] Component library chosen — **shadcn/ui** (ADR-001)
- [x] Document all environment variables (in CLAUDE.md Environment Variables section)
- [x] Create ADRs: ADR-001 through ADR-005

**Exit criteria:** All docs above exist and have been reviewed before Phase 1 starts.

---

### Phase 1 — Foundation (Single User, No Auth)

#### Sub-phase 1a — Project Scaffolding ✓ COMPLETE
- [x] Initialise Next.js 16 app with TypeScript + Tailwind v4 in `frontend/`
- [x] Install shadcn/ui with all required components
- [x] Initialise FastAPI app with uv in `backend/`
- [x] Backend health check endpoint passes tests
- [x] Configure ruff + mypy (backend), ESLint + tsc (frontend)
- [x] Set up GitHub Actions CI (`.github/workflows/ci.yml`)
- [ ] Connect Supabase project, run first migration (empty schema) ← next
- [ ] Deploy skeleton frontend to Vercel (blank page is fine)
- [ ] Deploy skeleton backend to Railway (health check endpoint only)

#### Sub-phase 1b — Database Schema & Core Models
- [ ] Create Supabase migrations for: `sources`, `targets`, `content`, `feedback`, `preferences`
- [ ] Write Pydantic models matching the schema
- [ ] Write SQLAlchemy models
- [ ] Seed database with initial sources (arXiv, GitHub)

#### Sub-phase 1c — First Fetcher (arXiv)
- [ ] Implement `backend/app/services/fetchers/arxiv.py`
- [ ] Uses arXiv public API (no scraping)
- [ ] Stores raw items in `content` table
- [ ] Write unit tests (mock HTTP calls)
- [ ] Write integration test against arXiv API sandbox

#### Sub-phase 1d — Summariser
- [ ] Implement `backend/app/services/summariser.py`
- [ ] Uses `claude-haiku-4-5` for cost efficiency
- [ ] Caches output by content hash (never re-summarise same item)
- [ ] Write unit tests (mock Claude API)

#### Sub-phase 1e — Basic Feed UI
- [ ] Next.js feed page renders content items from Supabase
- [ ] Card component: title, source, date, summary, link, thumbs up/down
- [ ] Mobile-first layout: single column on mobile, two columns on desktop
- [ ] Loading skeleton states
- [ ] Empty state

#### Sub-phase 1f — Feedback System
- [ ] Thumbs up / thumbs down stored in `feedback` table
- [ ] Basic feed re-ranks based on feedback (upvoted items rise)
- [ ] Feedback is instant and optimistic (UI updates immediately)

#### Sub-phase 1g — Remaining Fetchers
Add fetchers one at a time in this order (each with tests before implementation):
1. GitHub (GitHub REST API)
2. Reddit (Reddit JSON API — no auth needed for public subs)
3. Hacker News (Algolia HN API)
4. RSS feeds (blogs, newsletters — use `feedparser`)
5. Hugging Face (HF API)
6. Papers With Code (API)

#### Sub-phase 1h — Scheduler
- [ ] APScheduler runs all fetchers on configured cadence
- [ ] Default: daily at 6am UTC
- [ ] Configurable via environment variable `FETCH_CRON`
- [ ] Manual trigger endpoint: `POST /admin/trigger-fetch`

---

### Phase 2 — Source Management & Filtering

#### Sub-phase 2a — Sources Admin UI
- [ ] Page to view all sources and their targets
- [ ] Add / edit / archive sources and targets
- [ ] Set active / paused / archived status
- [ ] Trial mode for new sources (shown in "New Sources" section, not main feed)
- [ ] 5-star rating UI per source

#### Sub-phase 2b — Full Filter System
- [ ] Filter by content type, topic tag, source, date, read status
- [ ] Filter chips shown in persistent bar (dismissible with ×)
- [ ] Filters compose (AND logic)
- [ ] Bottom sheet filter panel on mobile
- [ ] Save filter combinations as named presets
- [ ] Keyword / free-text search

#### Sub-phase 2c — LLM Ranker
- [ ] Implement `backend/app/services/ranker.py`
- [ ] Uses `claude-sonnet-4-6` with user feedback history as context
- [ ] Produces a relevance score per content item
- [ ] Runs after each fetch cycle
- [ ] Write unit tests (mock Claude API and feedback data)

---

### Phase 3 — Personalization & UI Polish

#### Sub-phase 3a — Smarter Ranking
- [ ] Ranker incorporates: thumbs up rate, skip rate, save rate, source rating
- [ ] "More like this" and "Less like this" controls on each card
- [ ] Discovery assistant suggests new targets based on upvoted content

#### Sub-phase 3b — UI Polish
- [ ] Dark / light mode (persisted in preferences)
- [ ] Saved / bookmarked items section
- [ ] "Since last visit" badge on new items
- [ ] Notification for major model releases (configurable keywords)

---

### Phase 4 — Multi-User

#### Sub-phase 4a — Authentication
- [ ] Supabase Auth (email + Google OAuth)
- [ ] Protected routes in Next.js middleware
- [ ] Session management
- [ ] Per-user `preferences` and `feedback` rows (user_id FK)

#### Sub-phase 4b — User Profiles & Personalisation
- [ ] Each user has independent source list, targets, ratings
- [ ] Feed is fully personalised per user
- [ ] Admin user (you) retains ability to manage global source suggestions

---

### Phase 5 — Production Hardening
- [ ] Rate limiting on all API endpoints (FastAPI middleware)
- [ ] Redis caching layer for ranked feed (avoid DB hit on every page load)
- [ ] Sentry for error monitoring (frontend + backend)
- [ ] Uptime monitoring (Better Uptime or similar)
- [ ] Load testing
- [ ] Security audit (use `security-reviewer` agent)
- [ ] GDPR considerations if Phase 4 users are non-personal

---

## Skills & Agents — When to Use Each

Claude must activate the relevant skill or agent at each phase. Do not skip these.

### Before Writing Any New Feature
| Trigger | Action |
|---|---|
| Starting any new feature | Activate `search-first` skill — check for existing libraries first |
| Complex feature spanning multiple files | Activate `planner` agent — get a plan before coding |
| Architectural decision | Activate `architect` agent — document the decision as an ADR |

### Frontend Development
| Trigger | Skill / Agent |
|---|---|
| Writing React components | `frontend-patterns` skill |
| Building responsive/mobile UI | `frontend-patterns` skill — mobile-first section |
| TypeScript type errors | `build-error-resolver` agent |
| Adding forms or validation | `frontend-patterns` skill — forms section |
| Writing E2E tests | `e2e-testing` skill + `e2e-runner` agent |
| Code quality review | `coding-standards` skill + `code-reviewer` agent |

### Backend Development (Python)
| Trigger | Skill / Agent |
|---|---|
| Writing FastAPI endpoints | `api-design` skill + `backend-patterns` skill |
| Writing a new fetcher | `backend-patterns` skill — service layer section |
| Database schema / queries | `postgres-patterns` skill |
| Writing a migration | `database-migrations` skill |
| Reviewing SQL or migrations | `database-reviewer` agent |
| Caching LLM outputs | `content-hash-cache-pattern` skill |
| Building LLM pipeline (ranker/summariser) | `cost-aware-llm-pipeline` skill |
| Python code review | `python-reviewer` agent |
| Python tests | `python-testing` skill |
| Build/import errors | `build-error-resolver` agent |

### Testing (ALL features)
| Trigger | Skill / Agent |
|---|---|
| Before implementing any feature | `tdd-workflow` skill — write tests FIRST |
| New feature or bug fix | `tdd-guide` agent — use proactively |
| Coverage below 80% | `tdd-guide` agent |

### Security
| Trigger | Skill / Agent |
|---|---|
| Any endpoint that touches user data | `security-review` skill |
| Adding authentication (Phase 4) | `security-review` skill — auth section |
| End of every phase | `security-reviewer` agent — full audit |
| Committing any secrets-adjacent code | `security-scan` skill |

### Code Quality
| Trigger | Skill / Agent |
|---|---|
| After writing or changing code | `code-reviewer` agent — always |
| Before marking a sub-phase complete | `verification-loop` skill |
| Dead code / duplicate logic found | `refactor-cleaner` agent |
| Docs out of sync | `doc-updater` agent |

### Deployment & Ops
| Trigger | Skill / Agent |
|---|---|
| Setting up CI/CD | `deployment-patterns` skill |
| Docker needed | `docker-patterns` skill |
| Build pipeline broken | `build-error-resolver` agent |
| Background job architecture | `autonomous-loops` skill + `continuous-agent-loop` skill |

---

## Coding Standards

### TypeScript (Frontend)
- Strict mode always on (`"strict": true` in tsconfig)
- No `any` types — use `unknown` and narrow it
- All components have explicit prop types (interfaces, not inline)
- Use `const` always; `let` only when mutation is necessary
- File size limit: 400 lines. Split if larger.
- Function size limit: 50 lines. Extract if larger.
- No deep nesting — max 3 levels. Extract early returns.
- Immutable patterns — never mutate objects or arrays in place
- All async functions have explicit error handling
- Named exports only (no default exports except Next.js page components)

### Python (Backend)
- Python 3.12+
- Type hints on every function signature (input and return)
- Pydantic models for all request/response shapes
- No mutable default arguments
- Explicit error handling — never silent `except: pass`
- File size limit: 400 lines. Split into modules if larger.
- Function size limit: 50 lines.
- Use `dataclasses` or Pydantic for data containers, never plain dicts
- All external API calls wrapped in try/except with logging
- Environment variables loaded via `pydantic-settings` — never `os.getenv` directly

### Both
- No hardcoded values — use constants or environment variables
- No commented-out code committed to main
- Every public function has a docstring (one line minimum)
- Conventional commits: `feat:`, `fix:`, `refactor:`, `test:`, `chore:`, `docs:`

---

## Environment Variables

### Frontend (`frontend/.env.local`)
```
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
BACKEND_API_URL=           # Internal URL of the FastAPI service
NEXT_PUBLIC_APP_URL=       # Public URL of the frontend (for OG tags etc.)
```

### Backend (`backend/.env`)
```
DATABASE_URL=              # Supabase PostgreSQL connection string
SUPABASE_SERVICE_KEY=      # Service role key (never expose to frontend)
ANTHROPIC_API_KEY=         # Claude API key for ranking + summarisation
FETCH_CRON=0 6 * * *       # Cron expression for fetch schedule (default: 6am daily)
ENVIRONMENT=development    # development | staging | production
LOG_LEVEL=INFO
REDIS_URL=                 # Optional: Redis for caching (Phase 5)
```

**NEVER commit `.env` files. NEVER hardcode secrets. Always validate at startup that required variables are set.**

---

## Database Schema (Summary)

Full schema in `docs/data-model.md`. Summary:

```sql
sources         -- platforms and blogs (arXiv, GitHub, r/MachineLearning, etc.)
targets         -- specific handles/keywords/feeds within a source
content         -- fetched items (title, url, summary, score, status)
feedback        -- thumbs up/down, saves, skips per content item
preferences     -- user settings (refresh cadence, dark mode, etc.)
filter_presets  -- saved filter combinations
```

---

## API Design

Full spec in `docs/api-spec.md`. FastAPI base URL: `/api/v1/`

Key endpoint groups:
- `GET /feed` — ranked, filtered content feed
- `GET/POST/PATCH/DELETE /sources` — source management
- `GET/POST/PATCH/DELETE /sources/{id}/targets` — target management
- `POST /feedback` — thumbs up/down, save, skip
- `GET/POST /filter-presets` — saved filter views
- `GET/PATCH /preferences` — user settings
- `POST /admin/trigger-fetch` — manually trigger fetch cycle

---

## Common Commands

### Frontend
```bash
cd website/frontend
pnpm install            # Install dependencies
pnpm dev                # Start dev server (localhost:3000)
pnpm build              # Production build
pnpm lint               # ESLint
pnpm test               # Vitest unit tests
pnpm test:e2e           # Playwright E2E tests
pnpm type-check         # tsc --noEmit
```

### Backend
```bash
cd website/backend
uv sync                 # Install dependencies
uv run uvicorn app.main:app --reload  # Start dev server (localhost:8000)
uv run pytest           # Run all tests
uv run pytest --cov     # With coverage report
uv run alembic upgrade head  # Apply migrations
uv run alembic revision --autogenerate -m "description"  # New migration
```

### Supabase
```bash
supabase start          # Start local Supabase
supabase db reset       # Reset local DB and re-run migrations
supabase db push        # Push migrations to remote
```

---

## Before Marking Any Sub-Phase Complete

Run this checklist — do not skip steps:

- [ ] All tests pass (`pnpm test` and `uv run pytest`)
- [ ] Coverage is 80%+ (`uv run pytest --cov`)
- [ ] `pnpm type-check` passes with zero errors
- [ ] `pnpm lint` passes with zero warnings
- [ ] `code-reviewer` agent has reviewed all changed files
- [ ] `security-review` skill has been applied if auth/API/user data was touched
- [ ] `doc-updater` agent has updated any affected docs
- [ ] Feature works on mobile (test at 390px width)
- [ ] No `console.log` or `print()` debug statements committed
- [ ] No secrets or `.env` values hardcoded anywhere
- [ ] CLAUDE.md updated if the active phase changed

---

## What NOT to Do

- Do NOT use `npm` or `yarn` — use `pnpm` only
- Do NOT use `pip` — use `uv` only
- Do NOT use `any` in TypeScript
- Do NOT skip writing tests before implementation
- Do NOT skip the `code-reviewer` agent after writing code
- Do NOT use LLMs for data fetching — only for ranking and summarisation
- Do NOT store full article content — store title, summary, and link only
- Do NOT implement Phase N+1 before Phase N is fully verified
- Do NOT hardcode API keys, URLs, or secrets
- Do NOT write files longer than 400 lines — split them
- Do NOT mutate objects or state in place — always return new copies

---

## Open Decisions (Resolve in Phase 0)

- [x] **Project name** — **AIMeridian**
- [x] **Component library** — **shadcn/ui** (ADR-001)
- [x] **Background job runner** — **APScheduler** to start; migrate to Celery+Redis in Phase 5 if needed (ADR-002)
- [x] **LLM prompt templates** — see `docs/llm-prompts.md` (ADR-003)
- [x] **Content refresh cadence** — every 12 hours, 6:00 UTC + 18:00 UTC (ADR-004)
- [x] **X.com / LinkedIn strategy** — X API v2 Basic or RSSHub fallback; LinkedIn manual only (ADR-005)
- [ ] **Source quality review cadence** — quarterly suggested; confirm with user
