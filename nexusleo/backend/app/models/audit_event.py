"""Audit event model."""
from __future__ import annotations

from sqlalchemy import Column, DateTime, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.sql import func, text

from .base import Base


class AuditEvent(Base):
    """Represents a deterministic audit log entry."""

    __tablename__ = "audit_events"
    __table_args__ = (
        Index("ix_audit_event_case_id", "case_id"),
        Index("ix_audit_event_created_at", "created_at"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    case_id = Column(UUID(as_uuid=True), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False)
    actor = Column(String, nullable=False, server_default="system")
    action = Column(String, nullable=False)
    tool = Column(String, nullable=False)
    tool_version = Column(String, nullable=False)
    input_refs_json = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    output_refs_json = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
