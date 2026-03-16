# ADR-005: X.com and LinkedIn Data Strategy

**Status:** Accepted
**Date:** 2026-03-12
**Deciders:** Project owner

## Decision

### X.com
- Use **X API v2 Basic tier ($100/month)** if budget allows
- Otherwise use **RSSHub self-hosted** as a best-effort fallback
- Fetcher interface is designed to be swappable — the strategy can change without touching the pipeline

### LinkedIn
- **Do not scrape LinkedIn** (ToS violation, technically brittle)
- Provide **manual "Add Link"** feature (`POST /api/v1/content/manual`) for notable LinkedIn posts
- Defer automated LinkedIn fetching until a viable API option exists

## Rationale

**X.com:**
- Free tier is write-only — cannot read tweets
- Basic tier ($100/month) gives 10,000 tweets/month via search API — sufficient for 13 people × 30 tweets/month = ~400 tweets/month
- RSSHub (`https://github.com/DIYgod/RSSHub`) can proxy X profiles as RSS feeds when self-hosted, but reliability is inconsistent
- Nitter (public instances) is largely dead as of 2024; not a viable option

**LinkedIn:**
- The LinkedIn API requires an approved app and is restricted to the app owner's content
- Third-party RSS services (RSS.app, etc.) for LinkedIn are unreliable and often break
- Scraping violates LinkedIn's ToS and is legally risky
- Manual curation is sufficient for a personal tracker — LinkedIn posts are infrequent and high-signal

## Implementation Notes

- The `BaseFetcher` interface allows any fetcher to be swapped in
- X.com fetcher: `fetchers/twitter.py` — if no API key is configured, it returns an empty list with a log warning (graceful degradation)
- LinkedIn: no fetcher needed; content is added manually and flows through the normal summarise → rank pipeline

## Review Trigger

Revisit this decision if:
- X API pricing changes significantly
- A reliable, free X RSS bridge emerges
- LinkedIn opens a public read API
