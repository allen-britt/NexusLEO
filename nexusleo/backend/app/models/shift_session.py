"""Shift session model."""
from __future__ import annotations

from sqlalchemy import Column, DateTime, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from .base import Base


class ShiftSession(Base):
    """Represents a start/end bounded shift for a user."""

    __tablename__ = "shift_sessions"
    __table_args__ = (
        Index("ix_shift_session_user_id", "user_id"),
        Index("ix_shift_session_started_at", "started_at"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    ended_at = Column(DateTime(timezone=True), nullable=True)
    device_id = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
