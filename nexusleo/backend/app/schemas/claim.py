"""Claim response schemas."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from .mention import MentionOut


class ConfidenceOut(BaseModel):
    level: str
    rubric_version: str
    factors_json: dict
    rationale_text: str


class EvidenceOut(BaseModel):
    evidence_link_id: UUID
    weight: float
    notes: Optional[str] = None
    mention: MentionOut
    document_id: UUID


class ClaimOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    case_id: UUID
    claim_type: str
    predicate: str
    text: str
    subject_entity_id: Optional[UUID] = None
    object_entity_id: Optional[UUID] = None
    created_at: datetime
    confidence: Optional[ConfidenceOut] = None
    evidence: List[EvidenceOut]
    audit_event_ids: List[UUID]
