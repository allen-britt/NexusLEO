"""Attach activity to case schemas."""
from __future__ import annotations

from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel

from .claim import ClaimOut
from .ingest import IngestResult


class AttachActivityRequest(BaseModel):
    activity_log_entry_id: UUID
    actor: Optional[str] = None
    mode: str = "LINK_ONLY"


class AttachActivityResponse(BaseModel):
    case_id: UUID
    activity_log_entry_id: UUID
    mode: str
    linked: bool
    note_document_id: Optional[UUID] = None
    ingest_result: Optional[IngestResult] = None
    claims: List[ClaimOut]
    audit_event_id: UUID
