"""Case schemas."""
from __future__ import annotations

from datetime import datetime
from typing import Optional, Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CaseCreate(BaseModel):
    name: Optional[str] = None


class CaseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: Optional[str] = None
    created_at: datetime


class CaseStateContextIn(BaseModel):
    state_context: dict[str, Any]

    model_config = ConfigDict(extra="forbid")


class ObservedFactsIn(BaseModel):
    observed_facts: dict[str, Any]

    model_config = ConfigDict(extra="forbid")
