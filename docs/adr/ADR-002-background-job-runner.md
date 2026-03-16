# ADR-002: Background Job Runner

**Status:** Accepted
**Date:** 2026-03-12
**Deciders:** Project owner

## Decision

Use **APScheduler** for Phases 1–3. Evaluate Celery+Redis in Phase 5.

## Rationale

- APScheduler runs in-process inside FastAPI — zero additional infrastructure
- Simple cron configuration via `FETCH_CRON` environment variable
- Sufficient for a single-user app with one fetch cycle every 12 hours
- Railway does not natively support separate worker processes in the free tier

## Migration Trigger

Migrate to Celery+Redis if any of the following occur:
- A single fetch cycle exceeds 10 minutes
- Fetchers need to run in parallel across multiple workers
- Retry queues become necessary for reliability
- Multiple backend instances are deployed

## Consequences

- APScheduler is single-worker — if Railway restarts the process mid-job, the job is lost
- Mitigation: keep fetch cycles idempotent (upsert on content_hash conflict)
- No Flower dashboard for job monitoring — rely on logs instead
