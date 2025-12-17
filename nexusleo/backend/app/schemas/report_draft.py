from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel

from .case import CaseOut


class SourceRefOut(BaseModel):
    source_type: Literal["document", "activity", "audit_event", "claim"]
    source_id: UUID
    ts: Optional[datetime] = None


class ReportSectionOut(BaseModel):
    key: str
    title: str
    content_markdown: str
    source_refs: list[SourceRefOut]


class ReportDraftOut(BaseModel):
    case: CaseOut
    generated_at: datetime
    sections: list[ReportSectionOut]
