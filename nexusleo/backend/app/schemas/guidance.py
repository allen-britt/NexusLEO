"""Case procedural guidance schemas."""
from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel


class GuidanceItem(BaseModel):
    id: UUID
    category: Literal["documentation", "scene", "identity", "evidence", "reporting"]
    statement: str
    source: Literal["activity", "claim", "document", "timeline"]
    confidence: Literal["LOW", "MODERATE", "HIGH"]
    related_ids: list[UUID]


class CaseGuidanceResponse(BaseModel):
    case_id: UUID
    generated_at: datetime
    items: list[GuidanceItem]
