"""User schemas."""
from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class UserCreate(BaseModel):
    display_name: str
    badge_id: Optional[str] = None


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    display_name: str
    badge_id: Optional[str] = None
    created_at: datetime
