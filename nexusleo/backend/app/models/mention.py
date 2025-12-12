"""Mention model."""
from __future__ import annotations

from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from .base import Base


class Mention(Base):
    """Span-based mention extracted from documents."""

    __tablename__ = "mentions"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    document_id = Column(
        UUID(as_uuid=True),
        ForeignKey("source_documents.id", ondelete="CASCADE"),
        nullable=False,
    )
    text = Column(Text, nullable=False)
    start = Column(Integer, nullable=False)
    end = Column(Integer, nullable=False)
    speaker = Column(String, nullable=True)
    timestamp = Column(String, nullable=True)
    language = Column(String, nullable=True, default="en")
    entity_type_guess = Column(String, nullable=True)
