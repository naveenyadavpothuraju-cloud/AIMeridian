"""Pydantic schemas for Feedback, FilterPreset, and Preferences."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

# ── Feedback ──────────────────────────────────────────────────────────────────

VALID_FEEDBACK_TYPES = {"up", "down", "save", "skip", "more_like", "less_like"}


class FeedbackCreate(BaseModel):
    """Schema for recording a feedback interaction."""

    content_id: UUID
    feedback_type: str = Field(max_length=20)

    def model_post_init(self, __context: Any) -> None:
        """Validate feedback_type against allowed values."""
        if self.feedback_type not in VALID_FEEDBACK_TYPES:
            raise ValueError(f"feedback_type must be one of: {sorted(VALID_FEEDBACK_TYPES)}")


class FeedbackResponse(BaseModel):
    """Feedback record returned by the API."""

    id: UUID
    content_id: UUID
    feedback_type: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Filter Presets ────────────────────────────────────────────────────────────


class FilterPresetCreate(BaseModel):
    """Schema for saving a new filter preset."""

    name: str = Field(max_length=100)
    filters: dict[str, Any]
    is_default: bool = False


class FilterPresetUpdate(BaseModel):
    """Schema for updating a filter preset."""

    name: str | None = Field(default=None, max_length=100)
    filters: dict[str, Any] | None = None
    is_default: bool | None = None


class FilterPresetResponse(BaseModel):
    """Filter preset returned by the API."""

    id: UUID
    name: str
    filters: dict[str, Any]
    is_default: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── Preferences ───────────────────────────────────────────────────────────────


class PreferencesUpdate(BaseModel):
    """Schema for updating user preferences — any key-value pairs."""

    model_config = {"extra": "allow"}


class PreferencesResponse(BaseModel):
    """Flat map of all user preferences."""

    model_config = {"extra": "allow"}
