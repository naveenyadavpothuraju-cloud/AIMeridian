# Source Catalog — AIMeridian

**Version:** 1.0
**Phase:** 0 — Planning
**Last Updated:** 2026-03-12

This is the initial seed list of sources and targets to be inserted in Phase 1 (Sub-phase 1b.9).
Sources are organised by platform. Add new sources and targets here before seeding.

---

## arXiv

**Platform:** `arxiv`
**Fetch strategy:** arXiv public API (`http://export.arxiv.org/api/query`)
**Max results per fetch:** 50 per query

| Source Name | Category | Query | Rating |
|-------------|----------|-------|--------|
| arXiv cs.AI | research | `cs.AI` | 5 |
| arXiv cs.LG | research | `cs.LG` | 5 |
| arXiv cs.CL | research | `cs.CL` (NLP/LLMs) | 5 |
| arXiv cs.CV | research | `cs.CV` (Vision) | 3 |
| arXiv cs.RO | research | `cs.RO` (Robotics + AI) | 3 |

---

## GitHub

**Platform:** `github`
**Fetch strategy:** GitHub REST API — trending repos (via `created:>date` + `stars:>50` + topic), org activity
**Auth:** GitHub personal access token (optional; increases rate limit)

| Source Name | Category | Config | Rating |
|-------------|----------|--------|--------|
| GitHub Trending (AI) | tools | `{ "topics": ["artificial-intelligence", "llm", "machine-learning"], "min_stars": 100 }` | 5 |
| Anthropic GitHub | industry | `{ "org": "anthropics" }` | 5 |
| OpenAI GitHub | industry | `{ "org": "openai" }` | 5 |
| Google DeepMind GitHub | industry | `{ "org": "google-deepmind" }` | 5 |
| Meta AI GitHub | industry | `{ "org": "facebookresearch" }` | 4 |
| Mistral AI GitHub | industry | `{ "org": "mistralai" }` | 4 |
| Microsoft Research GitHub | industry | `{ "org": "microsoft" }` | 3 |
| Hugging Face GitHub | tools | `{ "org": "huggingface" }` | 5 |

---

## Reddit

**Platform:** `reddit`
**Fetch strategy:** Reddit JSON API (`https://www.reddit.com/r/{subreddit}/new.json`) — no auth required for public subs
**Sort:** `new` (most recent), limited to top 25 posts per fetch

| Source Name | Category | Subreddit | Rating |
|-------------|----------|-----------|--------|
| r/MachineLearning | community | `MachineLearning` | 5 |
| r/LocalLLaMA | community | `LocalLLaMA` | 5 |
| r/artificial | community | `artificial` | 3 |
| r/ArtificialIntelligence | community | `ArtificialIntelligence` | 3 |
| r/deeplearning | community | `deeplearning` | 4 |
| r/learnmachinelearning | community | `learnmachinelearning` | 3 |
| r/ChatGPT | community | `ChatGPT` | 2 |

---

## Hacker News

**Platform:** `hackernews`
**Fetch strategy:** Algolia HN Search API (`https://hn.algolia.com/api/v1/search`)
**Query:** tag-filtered searches for AI/ML content

| Source Name | Category | Query | Rating |
|-------------|----------|-------|--------|
| HN: Show HN AI | community | `{ "query": "AI machine learning", "tags": "show_hn", "min_points": 10 }` | 4 |
| HN: Ask HN AI | community | `{ "query": "AI LLM language model", "tags": "ask_hn", "min_points": 10 }` | 3 |
| HN: AI Stories | community | `{ "query": "large language model GPT Claude AI", "tags": "story", "min_points": 100 }` | 5 |

---

## HuggingFace

**Platform:** `huggingface`
**Fetch strategy:** HuggingFace Hub API (`https://huggingface.co/api/models`)
**Filter:** recently updated models with high downloads or trending

| Source Name | Category | Config | Rating |
|-------------|----------|--------|--------|
| HF Trending Models | tools | `{ "sort": "trending", "limit": 20 }` | 5 |
| HF New Datasets | research | `{ "type": "dataset", "sort": "lastModified", "limit": 10 }` | 3 |
| HF Spaces Trending | tools | `{ "type": "space", "sort": "trending", "limit": 10 }` | 3 |

---

## Papers With Code

**Platform:** `paperswithcode`
**Fetch strategy:** Papers With Code API (`https://paperswithcode.com/api/v1/`)

| Source Name | Category | Config | Rating |
|-------------|----------|--------|--------|
| PwC Latest Papers | research | `{ "endpoint": "papers", "ordering": "-published", "limit": 20 }` | 5 |
| PwC SOTA Methods | research | `{ "endpoint": "methods", "ordering": "-paper_date", "limit": 10 }` | 4 |

---

## RSS Feeds (Blogs & Newsletters)

**Platform:** `rss`
**Fetch strategy:** `feedparser` library — works with RSS 2.0 and Atom 1.0

| Source Name | Category | Feed URL | Rating |
|-------------|----------|----------|--------|
| Anthropic Blog | industry | `https://www.anthropic.com/news/rss.xml` | 5 |
| OpenAI Blog | industry | `https://openai.com/blog/rss.xml` | 5 |
| Google DeepMind Blog | industry | `https://deepmind.google/blog/rss.xml` | 5 |
| Hugging Face Blog | tools | `https://huggingface.co/blog/feed.xml` | 5 |
| Mistral AI Blog | industry | `https://mistral.ai/news/rss` | 4 |
| Cohere Blog | industry | `https://cohere.com/blog/rss` | 3 |
| Weights & Biases Blog | tools | `https://wandb.ai/blog/rss.xml` | 4 |
| Towards Data Science | community | `https://towardsdatascience.com/feed` | 3 |
| The Gradient | research | `https://thegradient.pub/rss/` | 4 |
| Import AI (Jack Clark) | newsletter | `https://jack-clark.net/feed/` | 5 |
| The Batch (deeplearning.ai) | newsletter | `https://www.deeplearning.ai/the-batch/feed/` | 4 |
| Ahead of AI (Sebastian Raschka) | newsletter | `https://magazine.sebastianraschka.com/feed` | 5 |
| Last Week in AI | newsletter | `https://lastweekin.ai/feed` | 4 |
| ML News (Yannic Kilcher) | community | `https://www.youtube.com/feeds/videos.xml?channel_id=UCZHmQk67mSJgfCCTn7xBfew` | 4 |

---

## X / Twitter (Conditional — ADR-005)

**Platform:** `twitter`
**Fetch strategy:** X API v2 Basic tier (if budget allows) OR RSSHub self-hosted fallback
**Status:** Deferred until ADR-005 decision is confirmed

### Key People to Track

| Name | Handle | Category |
|------|--------|----------|
| Sam Altman | `@sama` | industry |
| Andrej Karpathy | `@karpathy` | research |
| Yann LeCun | `@ylecun` | research |
| Dario Amodei | `@DarioAmodei` | industry |
| Ilya Sutskever | `@ilyasut` | research |
| Demis Hassabis | `@demishassabis` | industry |
| Emad Mostaque | `@EMostaque` | industry |
| Yoshua Bengio | `@yoshuabengio` | research |
| François Chollet | `@fchollet` | research |
| Jim Fan | `@DrJimFan` | research |
| Swyx | `@swyx` | community |
| Simon Willison | `@simonw` | tools |
| Ethan Mollick | `@emollick` | community |

### Key Organisations

| Name | Handle | Category |
|------|--------|----------|
| Anthropic | `@AnthropicAI` | industry |
| OpenAI | `@OpenAI` | industry |
| Google DeepMind | `@GoogleDeepMind` | industry |
| Mistral AI | `@MistralAI` | industry |
| Hugging Face | `@huggingface` | tools |
| Papers With Code | `@paperswithcode` | research |
| AI Alignment Forum | `@AIAlignment` | research |

---

## LinkedIn (Manual — ADR-005)

**Platform:** `linkedin`
**Fetch strategy:** Manual "Add Link" only (no automated fetching)
**Status:** Manual addition via `POST /api/v1/content/manual`

### Key Profiles to Watch (manually add notable posts)

| Name | Profile | Category |
|------|---------|----------|
| Andrew Ng | linkedin.com/in/andrewyng | research |
| Dario Amodei | linkedin.com/in/dario-amodei | industry |
| Jensen Huang | linkedin.com/in/jenhsunhuang | industry |
| Satya Nadella | linkedin.com/in/satyanadella | industry |

---

## YouTube (RSS via YouTube Feed API)

**Platform:** `rss`
**Fetch strategy:** YouTube channel RSS feed (`https://www.youtube.com/feeds/videos.xml?channel_id=...`)

| Source Name | Category | Channel ID | Rating |
|-------------|----------|------------|--------|
| Yannic Kilcher | research | `UCZHmQk67mSJgfCCTn7xBfew` | 5 |
| Two Minute Papers | research | `UCbfYPyITQ-7l4upoX8nvctg` | 4 |
| Andrej Karpathy | research | `UCXUPKJO5MZQMU11T6RGXbdg` | 5 |
| AI Explained | community | `UCNJ1Ymd5yFuUPtn21xtRbbw` | 4 |
| Sam Altman (talks) | industry | — | 3 |

---

## Seeding Notes

- All sources start with `status = 'active'` unless marked trial
- All targets start with `status = 'active'`
- Run `uv run python -m app.db.seed` after Phase 1b migrations to insert this catalog
- X.com and LinkedIn sources should be seeded with `status = 'paused'` until ADR-005 is resolved
