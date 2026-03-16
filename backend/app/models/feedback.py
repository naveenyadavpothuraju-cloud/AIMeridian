"""SQLAlchemy model for the feedback table."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.session import Base


class Feedback(Base):
    """User interaction with a content item (thumbs up/down, save, skip, more/less like)."""

    __tablename__ = "feedback"
    __table_args__ = (
        UniqueConstraint("content_id", "feedback_type", name="uq_feedback_content_type"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("content.id", ondelete="CASCADE"), nullable=False
    )
    feedback_type: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    # Relationships
    content: Mapped["Content"] = relationship("Content", back_populates="feedback_items")  # noqa: F821
