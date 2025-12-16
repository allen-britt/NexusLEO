"""Shift session schemas."""
from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class ShiftStartRequest(BaseModel):
    user_id: UUID
    device_id: Optional[str] = None


class ShiftStartResponse(BaseModel):
    shift_id: UUID


class ShiftEndResponse(BaseModel):
    shift_id: UUID
    ended_at: datetime
