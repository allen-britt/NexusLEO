from __future__ import annotations

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ArtifactCreateIn(BaseModel):
    kind: str
    label: str
    uri: str
    sha256: Optional[str] = None
    captured_at: Optional[datetime] = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    actor: Optional[str] = None


class ArtifactOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    case_id: UUID
    kind: str
    label: str
    uri: str
    sha256: Optional[str] = None
    captured_at: Optional[datetime] = None
    metadata_json: dict[str, Any]
    created_at: datetime
