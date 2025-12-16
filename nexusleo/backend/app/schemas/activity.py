"""Activity logging schemas."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ActivityLogCreate(BaseModel):
    entry_type: str
    text: str
    occurred_at: Optional[datetime] = None
    case_id: Optional[UUID] = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ActivityLogOut(BaseModel):
    id: UUID
    shift_id: UUID
    case_id: Optional[UUID] = None
    source_document_id: Optional[UUID] = None
    occurred_at: datetime
    entry_type: str
    text: str
    metadata_json: dict[str, Any]
    created_at: datetime
    timeline_item_type: str = "ACTIVITY_LOGGED"
