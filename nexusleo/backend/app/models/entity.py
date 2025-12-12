"""Entity model."""
from __future__ import annotations

from sqlalchemy import Column, DateTime, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.sql import func, text

from .base import Base


class Entity(Base):
    """Canonicalized entity candidate."""

    __tablename__ = "entities"
    __table_args__ = (Index("ix_entity_case_id", "case_id"),)

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    case_id = Column(UUID(as_uuid=True), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False)
    entity_type = Column(String, nullable=False)
    canonical_name = Column(String, nullable=False)
    attributes_json = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
