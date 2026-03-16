"""arXiv fetcher — pulls papers via the arXiv public Atom API."""

import logging
import re
from datetime import datetime
from xml.etree import ElementTree

import httpx

from app.services.fetchers.base import BaseFetcher, FetchedItem

logger = logging.getLogger(__name__)

ARXIV_API_URL = "http://export.arxiv.org/api/query"
ATOM_NS = "http://www.w3.org/2005/Atom"
RAW_TEXT_MAX_CHARS = 2000


class ArxivFetcher(BaseFetcher):
    """Fetches papers from arXiv using the public Atom/XML API."""

    def __init__(self, query: str, max_results: int = 50) -> None:
        self.query = query
        self.max_results = max_results

    def fetch(self) -> list[FetchedItem]:
        """Fetch papers from arXiv. Returns empty list on any error."""
        try:
            response = httpx.get(
                ARXIV_API_URL,
                params={
                    "search_query": f"cat:{self.query}",
                    "max_results": self.max_results,
                    "sortBy": "submittedDate",
                    "sortOrder": "descending",
                },
                timeout=30.0,
            )
            response.raise_for_status()
            return self._parse_response(response.text)
        except httpx.HTTPError as exc:
            logger.error("arXiv fetch failed: %s", exc)
            return []
        except Exception as exc:
            logger.error("arXiv unexpected error: %s", exc)
            return []

    def _parse_response(self, xml_text: str) -> list[FetchedItem]:
        """Parse arXiv Atom XML into FetchedItem objects."""
        try:
            root = ElementTree.fromstring(xml_text)
        except ElementTree.ParseError as exc:
            logger.error("arXiv XML parse error: %s", exc)
            return []

        items: list[FetchedItem] = []
        for entry in root.findall(f"{{{ATOM_NS}}}entry"):
            item = self._parse_entry(entry)
            if item is not None:
                items.append(item)
        return items

    def _parse_entry(self, entry: ElementTree.Element) -> FetchedItem | None:
        """Parse a single Atom <entry> element into a FetchedItem."""
        title_el = entry.find(f"{{{ATOM_NS}}}title")
        summary_el = entry.find(f"{{{ATOM_NS}}}summary")
        id_el = entry.find(f"{{{ATOM_NS}}}id")

        if title_el is None or id_el is None:
            return None

        title = (title_el.text or "").strip().replace("\n", " ")
        raw_text = (summary_el.text or "").strip().replace("\n", " ")[:RAW_TEXT_MAX_CHARS]
        arxiv_url = (id_el.text or "").strip()

        # Convert versioned ID to canonical URL: abs/XXXX.XXXXXvN → abs/XXXX.XXXXX
        canonical_url = re.sub(r"v\d+$", "", arxiv_url)

        # Extract arxiv_id from URL
        arxiv_id_match = re.search(r"abs/(\d{4}\.\d+)", canonical_url)
        arxiv_id = arxiv_id_match.group(1) if arxiv_id_match else ""

        # First author
        author_el = entry.find(f"{{{ATOM_NS}}}author/{{{ATOM_NS}}}name")
        author = author_el.text.strip() if author_el is not None and author_el.text else None

        # Published date
        published_el = entry.find(f"{{{ATOM_NS}}}published")
        published_at: datetime | None = None
        if published_el is not None and published_el.text:
            try:
                published_at = datetime.fromisoformat(published_el.text.replace("Z", "+00:00"))
            except ValueError:
                published_at = None

        if not title or not canonical_url:
            return None

        return FetchedItem(
            title=title,
            url=canonical_url,
            content_hash=FetchedItem.make_hash(title, canonical_url),
            raw_text=raw_text,
            content_type="paper",
            published_at=published_at,
            author=author,
            extra={"arxiv_id": arxiv_id},
        )
