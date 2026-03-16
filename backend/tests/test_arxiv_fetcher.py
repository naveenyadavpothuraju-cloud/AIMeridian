"""Tests for the arXiv fetcher — written FIRST (TDD red phase)."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.fetchers.arxiv import ArxivFetcher
from app.services.fetchers.base import FetchedItem


# ── Fixtures ──────────────────────────────────────────────────────────────────

SAMPLE_ARXIV_RESPONSE = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <id>http://arxiv.org/abs/2401.12345v1</id>
    <title>Attention Is All You Need: A Retrospective</title>
    <summary>We revisit the transformer architecture five years on.
    This paper presents new findings on scaling laws and attention patterns.</summary>
    <author><name>Jane Smith</name></author>
    <author><name>John Doe</name></author>
    <published>2024-01-15T00:00:00Z</published>
    <link href="http://arxiv.org/abs/2401.12345v1" rel="alternate" type="text/html"/>
    <category term="cs.AI"/>
    <category term="cs.LG"/>
  </entry>
  <entry>
    <id>http://arxiv.org/abs/2401.99999v2</id>
    <title>Another Paper Title</title>
    <summary>Abstract of the second paper with enough content to summarise.</summary>
    <author><name>Alice Brown</name></author>
    <published>2024-01-14T00:00:00Z</published>
    <link href="http://arxiv.org/abs/2401.99999v2" rel="alternate" type="text/html"/>
    <category term="cs.CL"/>
  </entry>
</feed>"""

EMPTY_ARXIV_RESPONSE = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
</feed>"""


@pytest.fixture
def fetcher() -> ArxivFetcher:
    """ArxivFetcher instance with default config."""
    return ArxivFetcher(query="cs.AI", max_results=50)


# ── Unit tests ────────────────────────────────────────────────────────────────

class TestArxivFetcherInit:
    def test_default_params(self, fetcher: ArxivFetcher) -> None:
        assert fetcher.query == "cs.AI"
        assert fetcher.max_results == 50

    def test_custom_params(self) -> None:
        f = ArxivFetcher(query="cs.LG cs.CL", max_results=10)
        assert f.query == "cs.LG cs.CL"
        assert f.max_results == 10


class TestArxivParsing:
    def test_parses_two_entries(self, fetcher: ArxivFetcher) -> None:
        items = fetcher._parse_response(SAMPLE_ARXIV_RESPONSE)
        assert len(items) == 2

    def test_parses_title(self, fetcher: ArxivFetcher) -> None:
        items = fetcher._parse_response(SAMPLE_ARXIV_RESPONSE)
        assert items[0].title == "Attention Is All You Need: A Retrospective"

    def test_parses_url_as_canonical(self, fetcher: ArxivFetcher) -> None:
        items = fetcher._parse_response(SAMPLE_ARXIV_RESPONSE)
        assert "2401.12345" in items[0].url

    def test_parses_author(self, fetcher: ArxivFetcher) -> None:
        items = fetcher._parse_response(SAMPLE_ARXIV_RESPONSE)
        assert items[0].author == "Jane Smith"

    def test_parses_published_at(self, fetcher: ArxivFetcher) -> None:
        items = fetcher._parse_response(SAMPLE_ARXIV_RESPONSE)
        assert items[0].published_at is not None
        assert items[0].published_at.year == 2024

    def test_parses_raw_text(self, fetcher: ArxivFetcher) -> None:
        items = fetcher._parse_response(SAMPLE_ARXIV_RESPONSE)
        assert "transformer" in items[0].raw_text.lower()

    def test_content_type_is_paper(self, fetcher: ArxivFetcher) -> None:
        items = fetcher._parse_response(SAMPLE_ARXIV_RESPONSE)
        assert items[0].content_type == "paper"

    def test_content_hash_is_sha256(self, fetcher: ArxivFetcher) -> None:
        items = fetcher._parse_response(SAMPLE_ARXIV_RESPONSE)
        assert len(items[0].content_hash) == 64  # SHA-256 hex = 64 chars

    def test_content_hash_is_deterministic(self, fetcher: ArxivFetcher) -> None:
        items1 = fetcher._parse_response(SAMPLE_ARXIV_RESPONSE)
        items2 = fetcher._parse_response(SAMPLE_ARXIV_RESPONSE)
        assert items1[0].content_hash == items2[0].content_hash

    def test_different_items_have_different_hashes(self, fetcher: ArxivFetcher) -> None:
        items = fetcher._parse_response(SAMPLE_ARXIV_RESPONSE)
        assert items[0].content_hash != items[1].content_hash

    def test_empty_feed_returns_empty_list(self, fetcher: ArxivFetcher) -> None:
        items = fetcher._parse_response(EMPTY_ARXIV_RESPONSE)
        assert items == []

    def test_raw_text_capped_at_2000_chars(self, fetcher: ArxivFetcher) -> None:
        items = fetcher._parse_response(SAMPLE_ARXIV_RESPONSE)
        assert len(items[0].raw_text) <= 2000

    def test_extra_contains_arxiv_id(self, fetcher: ArxivFetcher) -> None:
        items = fetcher._parse_response(SAMPLE_ARXIV_RESPONSE)
        assert "arxiv_id" in items[0].extra
        assert items[0].extra["arxiv_id"] == "2401.12345"


class TestArxivFetch:
    def test_fetch_calls_arxiv_api(self, fetcher: ArxivFetcher) -> None:
        with patch("httpx.get") as mock_get:
            mock_get.return_value = MagicMock(
                status_code=200,
                text=SAMPLE_ARXIV_RESPONSE,
                raise_for_status=MagicMock(),
            )
            items = fetcher.fetch()
            assert mock_get.called
            call_url = mock_get.call_args[0][0]
            params = mock_get.call_args.kwargs.get("params", {})
            assert "export.arxiv.org" in call_url
            assert "cs.AI" in str(params.get("search_query", ""))

    def test_fetch_returns_fetched_items(self, fetcher: ArxivFetcher) -> None:
        with patch("httpx.get") as mock_get:
            mock_get.return_value = MagicMock(
                status_code=200,
                text=SAMPLE_ARXIV_RESPONSE,
                raise_for_status=MagicMock(),
            )
            items = fetcher.fetch()
            assert len(items) == 2
            assert all(isinstance(i, FetchedItem) for i in items)

    def test_fetch_handles_http_error_gracefully(self, fetcher: ArxivFetcher) -> None:
        import httpx
        with patch("httpx.get") as mock_get:
            mock_get.side_effect = httpx.HTTPError("timeout")
            items = fetcher.fetch()
            assert items == []

    def test_fetch_respects_max_results(self) -> None:
        f = ArxivFetcher(query="cs.AI", max_results=5)
        with patch("httpx.get") as mock_get:
            mock_get.return_value = MagicMock(
                status_code=200,
                text=SAMPLE_ARXIV_RESPONSE,
                raise_for_status=MagicMock(),
            )
            f.fetch()
            params = mock_get.call_args.kwargs.get("params", {})
            assert params.get("max_results") == 5
