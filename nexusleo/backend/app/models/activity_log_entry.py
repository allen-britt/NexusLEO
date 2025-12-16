"""Activity log entry model."""
from __future__ import annotations

from sqlalchemy import Column, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.sql import func, text as sa_text

from .base import Base


class ActivityLogEntry(Base):
    """Represents a timestamped activity log entry within a shift."""

    __tablename__ = "activity_log_entries"
    __table_args__ = (
        Index("ix_activity_log_entry_shift_id", "shift_id"),
        Index("ix_activity_log_entry_case_id", "case_id"),
        Index("ix_activity_log_entry_source_document_id", "source_document_id"),
        Index("ix_activity_log_entry_occurred_at", "occurred_at"),
        Index("ix_activity_log_entry_created_at", "created_at"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    shift_id = Column(UUID(as_uuid=True), ForeignKey("shift_sessions.id", ondelete="CASCADE"), nullable=False)
    case_id = Column(UUID(as_uuid=True), ForeignKey("cases.id", ondelete="SET NULL"), nullable=True)
    source_document_id = Column(UUID(as_uuid=True), ForeignKey("source_documents.id", ondelete="SET NULL"), nullable=True)
    occurred_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    entry_type = Column(String, nullable=False)
    text = Column(Text, nullable=False)
    metadata_json = Column(JSONB, nullable=False, server_default=sa_text("'{}'::jsonb"))
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
