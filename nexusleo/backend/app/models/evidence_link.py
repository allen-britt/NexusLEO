"""Evidence link model."""
from __future__ import annotations

from sqlalchemy import Column, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from .base import Base


class EvidenceLink(Base):
    """Link between Claim and Mention."""

    __tablename__ = "evidence_links"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    claim_id = Column(UUID(as_uuid=True), ForeignKey("claims.id", ondelete="CASCADE"), nullable=False)
    mention_id = Column(UUID(as_uuid=True), ForeignKey("mentions.id", ondelete="CASCADE"), nullable=False)
    weight = Column(Float, nullable=False, default=1.0)
    notes = Column(String, nullable=True)
