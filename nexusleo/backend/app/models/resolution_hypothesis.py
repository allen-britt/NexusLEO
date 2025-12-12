"""Resolution hypothesis model."""
from __future__ import annotations

import enum

from sqlalchemy import Column, DateTime, Enum, Float, ForeignKey, Index
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.sql import func, text

from .base import Base


class ResolutionStatus(str, enum.Enum):
    UNREVIEWED = "UNREVIEWED"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"


class ResolutionHypothesis(Base):
    """Candidate entity alignment hypothesis plus review status."""

    __tablename__ = "resolution_hypotheses"
    __table_args__ = (
        Index("ix_resolution_hypothesis_mention_id", "mention_id"),
        Index("ix_resolution_hypothesis_candidate_entity_id", "candidate_entity_id"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    mention_id = Column(
        UUID(as_uuid=True),
        ForeignKey("mentions.id", ondelete="CASCADE"),
        nullable=False,
    )
    candidate_entity_id = Column(
        UUID(as_uuid=True),
        ForeignKey("entities.id", ondelete="CASCADE"),
        nullable=False,
    )
    score = Column(Float, nullable=False)
    features_json = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    status = Column(Enum(ResolutionStatus, name="resolution_hypothesis_status"), nullable=False, server_default=ResolutionStatus.UNREVIEWED.value)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
