"""Initial schema — sources, targets, content, feedback, preferences, filter_presets.

Revision ID: 001
Revises:
Create Date: 2026-03-16
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create all tables with indexes."""

    # ── sources ───────────────────────────────────────────────────────────────
    op.create_table(
        "sources",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("platform", sa.String(50), nullable=False),
        sa.Column("url", sa.Text, nullable=False),
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("rating", sa.SmallInteger, nullable=False, server_default="3"),
        sa.Column("fetch_config", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
    )
    op.create_index("idx_sources_status", "sources", ["status"])
    op.create_index("idx_sources_platform", "sources", ["platform"])
    op.create_index("idx_sources_category", "sources", ["category"])

    # ── targets ───────────────────────────────────────────────────────────────
    op.create_table(
        "targets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "source_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("sources.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("handle", sa.String(255), nullable=True),
        sa.Column("query", sa.Text, nullable=True),
        sa.Column("target_type", sa.String(50), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
    )
    op.create_index("idx_targets_source_id", "targets", ["source_id"])
    op.create_index("idx_targets_status", "targets", ["status"])

    # ── content ───────────────────────────────────────────────────────────────
    op.create_table(
        "content",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "source_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("sources.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "target_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("targets.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("title", sa.Text, nullable=False),
        sa.Column("url", sa.Text, nullable=False),
        sa.Column("content_hash", sa.String(64), nullable=False, unique=True),
        sa.Column("raw_text", sa.Text, nullable=True),
        sa.Column("summary", sa.Text, nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "fetched_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column("status", sa.String(20), nullable=False, server_default="raw"),
        sa.Column("relevance_score", sa.SmallInteger, nullable=True),
        sa.Column("content_type", sa.String(50), nullable=False, server_default="article"),
        sa.Column("topic_tags", postgresql.ARRAY(sa.String), nullable=False, server_default="{}"),
        sa.Column("author", sa.String(255), nullable=True),
        sa.Column("extra", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
    )
    op.create_index("idx_content_hash", "content", ["content_hash"], unique=True)
    op.create_index("idx_content_published_at", "content", [sa.text("published_at DESC")])
    op.create_index("idx_content_status", "content", ["status"])
    op.create_index("idx_content_source_id", "content", ["source_id"])
    op.create_index("idx_content_relevance_score", "content", [sa.text("relevance_score DESC")])
    op.create_index("idx_content_content_type", "content", ["content_type"])

    # Full-text search index (PostgreSQL tsvector)
    op.execute("""
        ALTER TABLE content ADD COLUMN fts tsvector
        GENERATED ALWAYS AS (
            to_tsvector('english',
                coalesce(title, '') || ' ' ||
                coalesce(summary, '') || ' ' ||
                coalesce(raw_text, '')
            )
        ) STORED
    """)
    op.execute("CREATE INDEX idx_content_fts ON content USING GIN(fts)")

    # ── feedback ──────────────────────────────────────────────────────────────
    op.create_table(
        "feedback",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "content_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("content.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("feedback_type", sa.String(20), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.UniqueConstraint("content_id", "feedback_type", name="uq_feedback_content_type"),
    )
    op.create_index("idx_feedback_content_id", "feedback", ["content_id"])
    op.create_index("idx_feedback_type", "feedback", ["feedback_type"])
    op.create_index("idx_feedback_created_at", "feedback", [sa.text("created_at DESC")])

    # ── preferences ───────────────────────────────────────────────────────────
    op.create_table(
        "preferences",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("key", sa.String(100), nullable=False),
        sa.Column("value", postgresql.JSONB, nullable=False),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.UniqueConstraint("key", name="uq_preferences_key"),
    )

    # ── filter_presets ────────────────────────────────────────────────────────
    op.create_table(
        "filter_presets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("filters", postgresql.JSONB, nullable=False),
        sa.Column("is_default", sa.Boolean, nullable=False, server_default="false"),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
    )


def downgrade() -> None:
    """Drop all tables in reverse order."""
    op.drop_table("filter_presets")
    op.drop_table("preferences")
    op.drop_table("feedback")
    op.drop_table("content")
    op.drop_table("targets")
    op.drop_table("sources")
