"""Pydantic schemas for Content items and feed queries."""

from datetime import date, datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class SourceSummary(BaseModel):
    """Minimal source info embedded in content responses."""

    id: UUID
    name: str
    platform: str

    model_config = {"from_attributes": True}


class FeedbackState(BaseModel):
    """Current feedback state for a content item."""

    up: bool = False
    down: bool = False
    saved: bool = False
    skipped: bool = False


class ContentResponse(BaseModel):
    """A single content item as returned by the feed API."""

    id: UUID
    title: str
    url: str
    summary: str | None
    content_type: str
    topic_tags: list[str]
    author: str | None
    published_at: datetime | None
    fetched_at: datetime
    relevance_score: int | None
    source: SourceSummary
    feedback: FeedbackState = Field(default_factory=FeedbackState)
    extra: dict[str, Any] = Field(default_factory=dict)

    model_config = {"from_attributes": True}


class ContentManualCreate(BaseModel):
    """Schema for manually adding a content item (e.g. LinkedIn post)."""

    url: str
    title: str = Field(max_length=500)
    content_type: str = Field(default="article", max_length=50)
    notes: str | None = None


class FeedQueryParams(BaseModel):
    """Query parameters for the feed endpoint."""

    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    content_type: list[str] | None = None
    topic_tags: list[str] | None = None
    source_ids: list[UUID] | None = None
    date_from: date | None = None
    date_to: date | None = None
    min_score: int = Field(default=0, ge=0, le=100)
    status_filter: str = Field(default="unread")
    search_query: str | None = None
    sort: str = Field(default="relevance")
