"""Tests for the Summariser service — written FIRST (TDD red phase)."""

from unittest.mock import MagicMock, patch
import uuid

import pytest

from app.services.summariser import Summariser


# ── Helpers ───────────────────────────────────────────────────────────────────


def _make_content(
    *,
    status: str = "raw",
    summary: str | None = None,
    title: str = "Test Paper Title",
    raw_text: str = "A paper about transformers and attention mechanisms.",
    content_type: str = "paper",
    source_name: str = "cs.AI",
    platform: str = "arXiv",
) -> MagicMock:
    """Build a mock Content ORM object."""
    item = MagicMock()
    item.id = uuid.uuid4()
    item.title = title
    item.raw_text = raw_text
    item.summary = summary
    item.status = status
    item.content_type = content_type
    item.source = MagicMock()
    item.source.name = source_name
    item.source.platform = platform
    return item


def _mock_anthropic_response(text: str) -> MagicMock:
    """Build a mock Anthropic Messages response."""
    msg = MagicMock()
    msg.content = [MagicMock(text=text)]
    return msg


# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture
def mock_client() -> MagicMock:
    """Mock Anthropic client."""
    client = MagicMock()
    client.messages.create.return_value = _mock_anthropic_response(
        "Transformers use attention to process sequences in parallel. "
        "This work introduces a new benchmark for evaluating attention patterns. "
        "Results show significant improvements over RNN baselines."
    )
    return client


@pytest.fixture
def summariser(mock_client: MagicMock) -> Summariser:
    return Summariser(client=mock_client)


# ── Unit tests ────────────────────────────────────────────────────────────────


class TestSummariserInit:
    def test_stores_client(self, mock_client: MagicMock) -> None:
        s = Summariser(client=mock_client)
        assert s.client is mock_client


class TestSummariseItem:
    def test_returns_string(self, summariser: Summariser, mock_client: MagicMock) -> None:
        result = summariser.summarise_item(
            title="Test",
            raw_text="Some abstract text.",
            content_type="paper",
            source_name="cs.AI",
            platform="arXiv",
        )
        assert isinstance(result, str)
        assert len(result) > 0

    def test_calls_haiku_model(self, summariser: Summariser, mock_client: MagicMock) -> None:
        summariser.summarise_item(
            title="Test",
            raw_text="Some abstract text.",
            content_type="paper",
            source_name="cs.AI",
            platform="arXiv",
        )
        call_kwargs = mock_client.messages.create.call_args.kwargs
        assert call_kwargs["model"] == "claude-haiku-4-5-20251001"

    def test_max_tokens_200(self, summariser: Summariser, mock_client: MagicMock) -> None:
        summariser.summarise_item(
            title="Test",
            raw_text="Some abstract text.",
            content_type="paper",
            source_name="cs.AI",
            platform="arXiv",
        )
        call_kwargs = mock_client.messages.create.call_args.kwargs
        assert call_kwargs["max_tokens"] == 200

    def test_temperature_zero(self, summariser: Summariser, mock_client: MagicMock) -> None:
        summariser.summarise_item(
            title="Test",
            raw_text="Some abstract text.",
            content_type="paper",
            source_name="cs.AI",
            platform="arXiv",
        )
        call_kwargs = mock_client.messages.create.call_args.kwargs
        assert call_kwargs.get("temperature", None) == 0

    def test_prompt_contains_title(self, summariser: Summariser, mock_client: MagicMock) -> None:
        summariser.summarise_item(
            title="My Unique Paper Title",
            raw_text="Some abstract text.",
            content_type="paper",
            source_name="cs.AI",
            platform="arXiv",
        )
        call_kwargs = mock_client.messages.create.call_args.kwargs
        user_content = call_kwargs["messages"][0]["content"]
        assert "My Unique Paper Title" in user_content

    def test_prompt_contains_raw_text(self, summariser: Summariser, mock_client: MagicMock) -> None:
        summariser.summarise_item(
            title="Test",
            raw_text="Distinctive abstract content XYZ.",
            content_type="paper",
            source_name="cs.AI",
            platform="arXiv",
        )
        call_kwargs = mock_client.messages.create.call_args.kwargs
        user_content = call_kwargs["messages"][0]["content"]
        assert "Distinctive abstract content XYZ." in user_content

    def test_prompt_contains_platform(self, summariser: Summariser, mock_client: MagicMock) -> None:
        summariser.summarise_item(
            title="Test",
            raw_text="Abstract.",
            content_type="paper",
            source_name="cs.AI",
            platform="arXiv",
        )
        call_kwargs = mock_client.messages.create.call_args.kwargs
        user_content = call_kwargs["messages"][0]["content"]
        assert "arXiv" in user_content

    def test_strips_whitespace_from_response(
        self, summariser: Summariser, mock_client: MagicMock
    ) -> None:
        mock_client.messages.create.return_value = _mock_anthropic_response("  Summary text.  ")
        result = summariser.summarise_item(
            title="Test",
            raw_text="Abstract.",
            content_type="paper",
            source_name="cs.AI",
            platform="arXiv",
        )
        assert result == "Summary text."

    def test_handles_api_error_returns_empty_string(
        self, summariser: Summariser, mock_client: MagicMock
    ) -> None:
        import anthropic

        mock_client.messages.create.side_effect = anthropic.APIError(
            message="rate limit", request=MagicMock(), body=None
        )
        result = summariser.summarise_item(
            title="Test",
            raw_text="Abstract.",
            content_type="paper",
            source_name="cs.AI",
            platform="arXiv",
        )
        assert result == ""


class TestRunBatch:
    def test_skips_already_summarised(
        self, summariser: Summariser, mock_client: MagicMock
    ) -> None:
        db = MagicMock()
        item = _make_content(status="summarised", summary="Existing summary.")
        count = summariser.run(db=db, items=[item])
        mock_client.messages.create.assert_not_called()
        assert count == 0

    def test_skips_items_with_failed_status(
        self, summariser: Summariser, mock_client: MagicMock
    ) -> None:
        db = MagicMock()
        item = _make_content(status="failed")
        summariser.run(db=db, items=[item])
        mock_client.messages.create.assert_not_called()

    def test_processes_raw_items(self, summariser: Summariser, mock_client: MagicMock) -> None:
        db = MagicMock()
        item = _make_content(status="raw")
        count = summariser.run(db=db, items=[item])
        mock_client.messages.create.assert_called_once()
        assert count == 1

    def test_sets_summary_on_content(self, summariser: Summariser, mock_client: MagicMock) -> None:
        db = MagicMock()
        item = _make_content(status="raw")
        summariser.run(db=db, items=[item])
        assert item.summary is not None
        assert len(item.summary) > 0

    def test_sets_status_to_summarised(
        self, summariser: Summariser, mock_client: MagicMock
    ) -> None:
        db = MagicMock()
        item = _make_content(status="raw")
        summariser.run(db=db, items=[item])
        assert item.status == "summarised"

    def test_commits_db_after_batch(self, summariser: Summariser, mock_client: MagicMock) -> None:
        db = MagicMock()
        items = [_make_content(status="raw"), _make_content(status="raw")]
        summariser.run(db=db, items=items)
        db.commit.assert_called_once()

    def test_processes_multiple_items(
        self, summariser: Summariser, mock_client: MagicMock
    ) -> None:
        db = MagicMock()
        items = [_make_content(status="raw") for _ in range(3)]
        count = summariser.run(db=db, items=items)
        assert mock_client.messages.create.call_count == 3
        assert count == 3

    def test_skips_item_with_empty_raw_text(
        self, summariser: Summariser, mock_client: MagicMock
    ) -> None:
        db = MagicMock()
        item = _make_content(status="raw", raw_text="")
        count = summariser.run(db=db, items=[item])
        mock_client.messages.create.assert_not_called()
        assert count == 0

    def test_marks_failed_when_api_errors(
        self, summariser: Summariser, mock_client: MagicMock
    ) -> None:
        import anthropic

        mock_client.messages.create.side_effect = anthropic.APIError(
            message="rate limit", request=MagicMock(), body=None
        )
        db = MagicMock()
        item = _make_content(status="raw")
        summariser.run(db=db, items=[item])
        assert item.status == "failed"

    def test_empty_items_list_returns_zero(
        self, summariser: Summariser, mock_client: MagicMock
    ) -> None:
        db = MagicMock()
        count = summariser.run(db=db, items=[])
        assert count == 0
        mock_client.messages.create.assert_not_called()

    def test_mixed_raw_and_summarised(
        self, summariser: Summariser, mock_client: MagicMock
    ) -> None:
        db = MagicMock()
        raw = _make_content(status="raw")
        done = _make_content(status="summarised", summary="Already done.")
        count = summariser.run(db=db, items=[raw, done])
        assert mock_client.messages.create.call_count == 1
        assert count == 1
