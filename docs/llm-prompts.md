# LLM Prompt Templates — AIMeridian

**Version:** 1.0
**Phase:** 0 — Planning
**Last Updated:** 2026-03-12

---

## Rules

- **Summarisation** uses `claude-haiku-4-5` (high volume, cost-sensitive)
- **Ranking** uses `claude-sonnet-4-6` (requires reasoning, lower volume)
- Every LLM call has a **token budget** and **timeout**
- Outputs are cached by content hash — never re-process the same content twice
- Prompts are versioned here; increment version when changing a prompt

---

## Prompt 1: Summarisation

**Model:** `claude-haiku-4-5`
**Version:** `sum-v1`
**Max input tokens:** ~800 (title + abstract capped at 2000 chars)
**Max output tokens:** 200
**Temperature:** 0 (deterministic)
**Timeout:** 10 seconds
**Cache key:** `sha256(title + raw_text)`

### System Prompt

```
You are a technical content summariser for AIMeridian, a personal AI developments tracker.
Your job is to write a concise, informative 2–3 sentence summary of the content provided.

Rules:
- Focus on: what is new, why it matters, and who it affects
- Do NOT include generic phrases like "this paper presents" or "the authors propose"
- Do NOT repeat the title
- Use plain English; avoid jargon unless it is standard in AI/ML
- Write in present tense
- Maximum 3 sentences
- Return only the summary — no preamble, no labels, no markdown
```

### User Prompt

```
Title: {title}
Source: {platform} — {source_name}
Content type: {content_type}

{raw_text}
```

### Example Input

```
Title: LLaMA 3: Open Foundation and Fine-Tuned Chat Models
Source: arXiv — cs.AI
Content type: paper

We introduce LLaMA 3, a new set of foundation language models ranging from 8B to 70B parameters.
LLaMA 3 is trained on over 15T tokens of public data and demonstrates strong performance on
standard benchmarks while remaining fully open source. Our fine-tuned Instruct variants achieve
performance comparable to closed-source models on human preference evaluations...
```

### Example Output

```
Meta releases LLaMA 3, an open-source language model family (8B–70B parameters) trained on 15 trillion
tokens that matches closed-source model performance on human preference benchmarks. Unlike previous
open models, LLaMA 3 Instruct variants are competitive with GPT-4 class models on coding and reasoning
tasks. Full weights and training details are publicly available.
```

---

## Prompt 2: Ranking

**Model:** `claude-sonnet-4-6`
**Version:** `rank-v1`
**Max input tokens:** ~6000 (50 items + feedback context)
**Max output tokens:** 4000
**Temperature:** 0 (deterministic)
**Timeout:** 60 seconds
**Cache key:** `sha256(sorted(content_ids) + feedback_version)`
**Batch size:** 50 items per call

### System Prompt

```
You are a relevance ranker for AIMeridian, a personal AI developments tracker.
Your job is to score each content item by how relevant and interesting it is to the user,
based on their feedback history.

Scoring rules:
- Score each item 0–100 where:
  100 = Exactly what the user wants; highly relevant and novel
  75  = Very relevant; user would likely read this
  50  = Moderately relevant; some signal of interest
  25  = Marginally relevant; weak match to user interests
  0   = Irrelevant or redundant to the user's interests
- Higher scores for: topics the user has upvoted, sources the user rated highly,
  authors/orgs the user follows, novel findings (not rehashed content)
- Lower scores for: topics the user has downvoted, sources rated poorly,
  duplicate or low-effort content, content types the user consistently skips
- A user's explicit "more_like_this" signal on an item should boost similar content by ~15 points
- A user's explicit "less_like_this" signal should penalise similar content by ~15 points

Output format:
Return a JSON array — one object per item — with no preamble or markdown:
[
  {"id": "<content_id>", "score": <0-100>, "reason": "<one sentence>"},
  ...
]
```

### User Prompt

```
## User Feedback Context

### Topics user frequently upvotes (strong positive signal):
{upvoted_topics}

### Topics user frequently downvotes (strong negative signal):
{downvoted_topics}

### Sources rated 4–5 stars (preferred sources):
{high_rated_sources}

### Sources rated 1–2 stars (disliked sources):
{low_rated_sources}

### "More like this" signals (recent):
{more_like_signals}

### "Less like this" signals (recent):
{less_like_signals}

---

## Content Items to Rank

{content_items_json}
```

### Feedback Context Format

`{upvoted_topics}` — top 20 topic tags by upvote frequency, e.g.:
```
- llm-fine-tuning (upvoted 14 times)
- reasoning-models (upvoted 11 times)
- multimodal (upvoted 8 times)
```

`{content_items_json}` — JSON array, one object per item:
```json
[
  {
    "id": "uuid-1",
    "title": "Scaling Laws for Neural Language Models",
    "content_type": "paper",
    "topic_tags": ["scaling", "llm", "training"],
    "source": "arXiv cs.AI",
    "published_at": "2026-03-10",
    "summary": "OpenAI presents empirical scaling laws..."
  }
]
```

### Example Output

```json
[
  {
    "id": "uuid-1",
    "score": 82,
    "reason": "Scaling laws directly relate to LLM training which the user frequently upvotes."
  },
  {
    "id": "uuid-2",
    "score": 34,
    "reason": "Computer vision paper; user has consistently downvoted non-NLP research."
  }
]
```

---

## Prompt 3: Topic Tag Inference (Optional, Phase 2+)

**Model:** `claude-haiku-4-5`
**Version:** `tags-v1`
**Max output tokens:** 50
**Temperature:** 0
**When used:** After summarisation, if `topic_tags` is empty
**Cache key:** same as summarisation (`sha256(title + raw_text)`)

### System Prompt

```
You are a topic tagger for an AI developments tracker.
Given a content item, return up to 5 relevant topic tags.

Rules:
- Use lowercase, hyphenated slugs (e.g., "llm-fine-tuning", "multi-agent", "computer-vision")
- Choose from common AI/ML topics; do not invent obscure tags
- Return only a JSON array of strings — no preamble, no markdown:
["tag1", "tag2", "tag3"]
```

### User Prompt

```
Title: {title}
Summary: {summary}
Content type: {content_type}
```

### Example Output

```json
["llm", "fine-tuning", "instruction-tuning", "rlhf"]
```

---

## Cost Budget Reference

| Prompt | Model | Avg input tokens | Avg output tokens | Cost per call (approx) |
|--------|-------|-----------------|-------------------|----------------------|
| Summarisation | haiku-4-5 | ~600 | ~150 | ~$0.0002 |
| Ranking (50 items) | sonnet-4-6 | ~5000 | ~3000 | ~$0.05 |
| Tag inference | haiku-4-5 | ~200 | ~30 | ~$0.00005 |

**Estimated daily cost** (100 new items/day):
- Summarisation: 100 × $0.0002 = **$0.02**
- Ranking: 2 batches × $0.05 = **$0.10**
- Tags: 100 × $0.00005 = **$0.005**
- **Total: ~$0.125/day → ~$4/month**

Caching eliminates re-processing costs for duplicate items.

---

## Prompt Versioning

When a prompt is updated:
1. Increment the version slug (e.g., `sum-v1` → `sum-v2`)
2. Update this file
3. Add a migration note below

### Changelog

| Version | Date | Change |
|---------|------|--------|
| `sum-v1` | 2026-03-12 | Initial summarisation prompt |
| `rank-v1` | 2026-03-12 | Initial ranking prompt |
| `tags-v1` | 2026-03-12 | Initial tag inference prompt |
