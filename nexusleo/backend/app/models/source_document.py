"""Source document model."""
from __future__ import annotations

from sqlalchemy import Column, DateTime, ForeignKey, Index, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.sql import func, text

from .base import Base


class SourceDocument(Base):
    """Ingested source document for a case."""

    __tablename__ = "source_documents"
    __table_args__ = (
        UniqueConstraint("case_id", "sha256", name="uq_source_document_case_sha"),
        Index("ix_source_document_case_id", "case_id"),
        Index("ix_source_document_sha256", "sha256"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    case_id = Column(UUID(as_uuid=True), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False)
    type = Column(String, nullable=False)
    sha256 = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    metadata_json = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    raw_text = Column(Text, nullable=False)
