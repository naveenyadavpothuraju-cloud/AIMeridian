# ADR-004: Content Refresh Cadence

**Status:** Accepted
**Date:** 2026-03-12
**Deciders:** Project owner

## Decision

- Default fetch cadence: **every 12 hours** (6:00 UTC and 18:00 UTC)
- Configurable via `FETCH_CRON` environment variable
- Manual trigger always available via `POST /api/v1/admin/trigger-fetch`

## Rationale

- Daily fetching (once) misses breaking news; hourly is too aggressive for rate limits and LLM costs
- 12 hours is a good balance: fresh enough for daily use, cheap enough to run indefinitely
- arXiv, GitHub, and HN publish throughout the day — catching two windows covers most new content
- Manual trigger covers urgent needs (e.g., a major model release mid-day)

## Per-Source Overrides (Phase 2+)

Some sources benefit from more frequent fetching:
- Hacker News: every 4 hours (high volume, fast-moving)
- Reddit: every 6 hours
- arXiv: daily (publishes on a fixed schedule)

These can be set in `sources.fetch_config` as `{ "cron_override": "0 */4 * * *" }` once the scheduler supports per-source crons.

## Consequences

- The `FETCH_CRON` env variable must be set on Railway
- Default: `0 6,18 * * *`
- A missed fetch (Railway restart) is not critical — next scheduled run will catch up
