"""Document schemas."""
from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DocumentCreate(BaseModel):
    type: str = "TRANSCRIPT"
    text: str
    metadata: dict = Field(default_factory=dict)


class DocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    case_id: UUID
    type: str
    sha256: str
    created_at: datetime
    metadata_json: dict
