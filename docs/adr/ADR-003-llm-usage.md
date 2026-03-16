# ADR-003: LLM Usage Strategy

**Status:** Accepted
**Date:** 2026-03-12
**Deciders:** Project owner

## Decision

- Use **claude-haiku-4-5** for summarisation
- Use **claude-sonnet-4-6** for ranking
- LLMs are **never** used for data fetching
- All LLM outputs are cached by content hash

## Rationale

**Fetching via APIs is strictly better than LLMs for data retrieval:**
- APIs return structured, accurate, real-time data
- LLMs cannot browse the web in real time (without tools)
- API cost is zero or trivial; LLM cost scales with volume

**Model selection:**
- Haiku is used for summarisation because it is called once per content item (high volume). It produces excellent 2–3 sentence summaries at ~$0.0002/call.
- Sonnet is used for ranking because it needs to reason about user preferences and produce nuanced scores. It runs in batches of 50 items (~$0.05/batch).

**Caching:**
- Summarisation is cached by `sha256(title + raw_text)` — the same paper from two different fetchers will never be re-summarised
- Ranking is cached by `sha256(sorted(content_ids) + feedback_version)` — re-ranking only occurs when content or user feedback changes

## Cost Estimate

~$4/month at 100 new items/day. See `docs/llm-prompts.md` for breakdown.

## Consequences

- Prompt changes require cache invalidation (increment prompt version in `docs/llm-prompts.md`)
- Token budgets and timeouts must be enforced on every call
- Never expose `ANTHROPIC_API_KEY` to the frontend
