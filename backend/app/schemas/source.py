"""Pydantic schemas for Source and Target resources."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

# ── Target schemas ────────────────────────────────────────────────────────────


class TargetBase(BaseModel):
    """Fields common to create and update operations."""

    name: str = Field(max_length=255)
    handle: str | None = Field(default=None, max_length=255)
    query: str | None = None
    target_type: str = Field(max_length=50)
    status: str = Field(default="active", max_length=20)
    notes: str | None = None


class TargetCreate(TargetBase):
    """Schema for creating a new target."""


class TargetUpdate(BaseModel):
    """Schema for partial target update — all fields optional."""

    name: str | None = Field(default=None, max_length=255)
    handle: str | None = Field(default=None, max_length=255)
    query: str | None = None
    target_type: str | None = Field(default=None, max_length=50)
    status: str | None = Field(default=None, max_length=20)
    notes: str | None = None


class TargetResponse(TargetBase):
    """Schema returned by the API."""

    id: UUID
    source_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── Source schemas ────────────────────────────────────────────────────────────


class SourceBase(BaseModel):
    """Fields common to create and update operations."""

    name: str = Field(max_length=255)
    platform: str = Field(max_length=50)
    url: str
    category: str = Field(max_length=50)
    description: str | None = None
    status: str = Field(default="active", max_length=20)
    rating: int = Field(default=3, ge=1, le=5)
    fetch_config: dict[str, Any] = Field(default_factory=dict)


class SourceCreate(SourceBase):
    """Schema for creating a new source."""


class SourceUpdate(BaseModel):
    """Schema for partial source update — all fields optional."""

    name: str | None = Field(default=None, max_length=255)
    url: str | None = None
    category: str | None = Field(default=None, max_length=50)
    description: str | None = None
    status: str | None = Field(default=None, max_length=20)
    rating: int | None = Field(default=None, ge=1, le=5)
    fetch_config: dict[str, Any] | None = None


class SourceResponse(SourceBase):
    """Schema returned by the API — includes target count."""

    id: UUID
    target_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SourceDetailResponse(SourceResponse):
    """Source response with nested targets list."""

    targets: list[TargetResponse] = []
