"""Base fetcher interface — all source fetchers must implement this."""

import hashlib
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class FetchedItem:
    """A single raw item returned by a fetcher before DB storage."""

    title: str
    url: str
    content_hash: str
    raw_text: str
    content_type: str
    published_at: datetime | None = None
    author: str | None = None
    extra: dict = field(default_factory=dict)

    @staticmethod
    def make_hash(title: str, url: str) -> str:
        """Produce a deterministic SHA-256 hash from title + url."""
        payload = f"{title.strip()}{url.strip()}".encode()
        return hashlib.sha256(payload).hexdigest()


class BaseFetcher(ABC):
    """Abstract base for all content fetchers."""

    @abstractmethod
    def fetch(self) -> list[FetchedItem]:
        """Fetch items from the source. Returns empty list on error — never raises."""
        ...
