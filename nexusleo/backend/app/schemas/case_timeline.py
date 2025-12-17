"""Case timeline read schemas."""
from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel


class DocumentMini(BaseModel):
    document_id: UUID
    document_type: str
    sha256: str


class AuditMini(BaseModel):
    audit_event_id: UUID
    action: str
    actor: str
    tool: str
    tool_version: str


class ClaimMini(BaseModel):
    claim_id: UUID
    predicate: str
    text: str
    confidence_level: Optional[str] = None


class ActivityMini(BaseModel):
    activity_id: UUID
    shift_id: UUID
    officer_user_id: Optional[UUID] = None
    entry_type: str
    text: str
    source_document_id: Optional[UUID] = None


class ArtifactMini(BaseModel):
    artifact_id: UUID
    kind: str
    label: str
    sha256: Optional[str] = None
    captured_at: Optional[datetime] = None


class CaseTimelineItem(BaseModel):
    ts: datetime
    item_type: Literal["DOCUMENT_ADDED", "AUDIT_EVENT", "CLAIM_CREATED", "ACTIVITY_ATTACHED", "ARTIFACT_ADDED"]

    document: Optional[DocumentMini] = None
    audit: Optional[AuditMini] = None
    claim: Optional[ClaimMini] = None
    activity: Optional[ActivityMini] = None
    artifact: Optional[ArtifactMini] = None
