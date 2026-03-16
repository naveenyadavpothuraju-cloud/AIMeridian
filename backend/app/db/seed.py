"""Seed the database with initial sources and targets from the source catalog."""

import uuid

from sqlalchemy.orm import Session

import app.models  # noqa: F401 — registers all models so relationships resolve
from app.db.session import SessionLocal
from app.models.source import Source
from app.models.target import Target

SOURCES: list[dict] = [
    # arXiv
    {
        "name": "arXiv cs.AI",
        "platform": "arxiv",
        "url": "https://arxiv.org",
        "category": "research",
        "status": "active",
        "rating": 5,
        "fetch_config": {"query": "cs.AI", "max_results": 50},
        "targets": [{"name": "cs.AI category", "query": "cs.AI", "target_type": "topic"}],
    },
    {
        "name": "arXiv cs.LG",
        "platform": "arxiv",
        "url": "https://arxiv.org",
        "category": "research",
        "status": "active",
        "rating": 5,
        "fetch_config": {"query": "cs.LG", "max_results": 50},
        "targets": [{"name": "cs.LG category", "query": "cs.LG", "target_type": "topic"}],
    },
    {
        "name": "arXiv cs.CL",
        "platform": "arxiv",
        "url": "https://arxiv.org",
        "category": "research",
        "status": "active",
        "rating": 5,
        "fetch_config": {"query": "cs.CL", "max_results": 50},
        "targets": [{"name": "cs.CL (NLP/LLMs)", "query": "cs.CL", "target_type": "topic"}],
    },
    # GitHub
    {
        "name": "GitHub Trending (AI)",
        "platform": "github",
        "url": "https://github.com",
        "category": "tools",
        "status": "active",
        "rating": 5,
        "fetch_config": {
            "topics": ["artificial-intelligence", "llm", "machine-learning"],
            "min_stars": 100,
        },
        "targets": [
            {"name": "AI trending repos", "query": "llm machine-learning", "target_type": "topic"}
        ],
    },
    {
        "name": "Anthropic GitHub",
        "platform": "github",
        "url": "https://github.com/anthropics",
        "category": "industry",
        "status": "active",
        "rating": 5,
        "fetch_config": {"org": "anthropics"},
        "targets": [{"name": "anthropics org", "handle": "anthropics", "target_type": "org"}],
    },
    {
        "name": "Hugging Face GitHub",
        "platform": "github",
        "url": "https://github.com/huggingface",
        "category": "tools",
        "status": "active",
        "rating": 5,
        "fetch_config": {"org": "huggingface"},
        "targets": [{"name": "huggingface org", "handle": "huggingface", "target_type": "org"}],
    },
    # Reddit
    {
        "name": "r/MachineLearning",
        "platform": "reddit",
        "url": "https://reddit.com/r/MachineLearning",
        "category": "community",
        "status": "active",
        "rating": 5,
        "fetch_config": {"subreddit": "MachineLearning"},
        "targets": [
            {"name": "r/MachineLearning", "handle": "MachineLearning", "target_type": "topic"}
        ],
    },
    {
        "name": "r/LocalLLaMA",
        "platform": "reddit",
        "url": "https://reddit.com/r/LocalLLaMA",
        "category": "community",
        "status": "active",
        "rating": 5,
        "fetch_config": {"subreddit": "LocalLLaMA"},
        "targets": [{"name": "r/LocalLLaMA", "handle": "LocalLLaMA", "target_type": "topic"}],
    },
    # Hacker News
    {
        "name": "Hacker News (AI)",
        "platform": "hackernews",
        "url": "https://news.ycombinator.com",
        "category": "community",
        "status": "active",
        "rating": 5,
        "fetch_config": {
            "query": "large language model GPT Claude AI",
            "tags": "story",
            "min_points": 100,
        },
        "targets": [{"name": "HN AI stories", "query": "AI LLM", "target_type": "topic"}],
    },
    # HuggingFace
    {
        "name": "HuggingFace Trending",
        "platform": "huggingface",
        "url": "https://huggingface.co",
        "category": "tools",
        "status": "active",
        "rating": 5,
        "fetch_config": {"sort": "trending", "limit": 20},
        "targets": [{"name": "Trending models", "query": "trending", "target_type": "topic"}],
    },
    # Papers With Code
    {
        "name": "Papers With Code",
        "platform": "paperswithcode",
        "url": "https://paperswithcode.com",
        "category": "research",
        "status": "active",
        "rating": 5,
        "fetch_config": {"endpoint": "papers", "ordering": "-published", "limit": 20},
        "targets": [{"name": "Latest papers", "query": "latest", "target_type": "topic"}],
    },
    # RSS Blogs
    {
        "name": "Anthropic Blog",
        "platform": "rss",
        "url": "https://www.anthropic.com/news/rss.xml",
        "category": "industry",
        "status": "active",
        "rating": 5,
        "fetch_config": {"feed_url": "https://www.anthropic.com/news/rss.xml"},
        "targets": [{"name": "Anthropic News", "handle": "anthropic", "target_type": "org"}],
    },
    {
        "name": "OpenAI Blog",
        "platform": "rss",
        "url": "https://openai.com/blog/rss.xml",
        "category": "industry",
        "status": "active",
        "rating": 5,
        "fetch_config": {"feed_url": "https://openai.com/blog/rss.xml"},
        "targets": [{"name": "OpenAI Blog", "handle": "openai", "target_type": "org"}],
    },
    {
        "name": "Import AI (Jack Clark)",
        "platform": "rss",
        "url": "https://jack-clark.net/feed/",
        "category": "newsletter",
        "status": "active",
        "rating": 5,
        "fetch_config": {"feed_url": "https://jack-clark.net/feed/"},
        "targets": [
            {"name": "Import AI newsletter", "handle": "jack-clark", "target_type": "person"}
        ],
    },
    {
        "name": "Ahead of AI (Raschka)",
        "platform": "rss",
        "url": "https://magazine.sebastianraschka.com/feed",
        "category": "newsletter",
        "status": "active",
        "rating": 5,
        "fetch_config": {"feed_url": "https://magazine.sebastianraschka.com/feed"},
        "targets": [{"name": "Ahead of AI", "handle": "sebastianraschka", "target_type": "person"}],
    },
]


def seed(db: Session) -> None:
    """Insert all sources and targets. Skip existing (upsert by name + platform)."""
    for src_data in SOURCES:
        targets_data: list[dict] = src_data.pop("targets", [])

        existing = (
            db.query(Source).filter_by(name=src_data["name"], platform=src_data["platform"]).first()
        )

        if existing:
            source = existing
        else:
            source = Source(id=uuid.uuid4(), **src_data)
            db.add(source)
            db.flush()

        for t in targets_data:
            exists = db.query(Target).filter_by(source_id=source.id, name=t["name"]).first()
            if not exists:
                db.add(Target(id=uuid.uuid4(), source_id=source.id, **t))

    db.commit()
    print(f"Seeded {len(SOURCES)} sources.")


if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed(db)
    finally:
        db.close()
