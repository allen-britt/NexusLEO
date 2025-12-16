"""Shift log note schemas."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel

from .activity import ActivityLogOut
from .claim import ClaimOut
from .document import DocumentOut
from .ingest import IngestResult


class ShiftLogNoteCreate(BaseModel):
    entry_type: str
    text: str
    occurred_at: Optional[datetime] = None
    case_id: Optional[UUID] = None
    actor: Optional[str] = None


class ShiftLogNoteOut(BaseModel):
    activity_log_entry: ActivityLogOut
    document: DocumentOut
    ingest_result: IngestResult
    claims: List[ClaimOut]
