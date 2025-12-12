"""Confidence assessment model."""
from __future__ import annotations

import enum

from sqlalchemy import Column, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.sql import func

from .base import Base


class ConfidenceLevel(str, enum.Enum):
    HIGH = "HIGH"
    MODERATE = "MODERATE"
    LOW = "LOW"


class ConfidenceAssessment(Base):
    """Confidence rubric result per claim."""

    __tablename__ = "confidence_assessments"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    claim_id = Column(
        UUID(as_uuid=True),
        ForeignKey("claims.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    level = Column(Enum(ConfidenceLevel, name="confidence_level"), nullable=False)
    rubric_version = Column(String, nullable=False)
    factors_json = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    rationale_text = Column(Text, nullable=False)
