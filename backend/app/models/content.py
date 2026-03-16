"""SQLAlchemy model for the content table."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, SmallInteger, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.session import Base


class Content(Base):
    """A fetched content item — paper, repo, post, article, model release, etc."""

    __tablename__ = "content"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sources.id", ondelete="CASCADE"), nullable=False
    )
    target_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("targets.id", ondelete="SET NULL"), nullable=True
    )
    title: Mapped[str] = mapped_column(Text, nullable=False)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="raw")
    relevance_score: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    content_type: Mapped[str] = mapped_column(String(50), nullable=False, default="article")
    topic_tags: Mapped[list[str]] = mapped_column(
        ARRAY(String),
        nullable=False,
        default=list,  # type: ignore[arg-type]
    )
    author: Mapped[str | None] = mapped_column(String(255), nullable=True)
    extra: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    source: Mapped["Source"] = relationship("Source", back_populates="content_items")  # noqa: F821
    target: Mapped["Target | None"] = relationship(  # noqa: F821
        "Target", back_populates="content_items"
    )
    feedback_items: Mapped[list["Feedback"]] = relationship(  # noqa: F821
        "Feedback", back_populates="content", cascade="all, delete-orphan"
    )
