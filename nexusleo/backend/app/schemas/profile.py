"""Profile schemas."""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class ProfileOut(BaseModel):
    profile_id: str
    name: str
    scope: str
    jurisdiction: str
    version: str
    guidance_categories: list[str]
    notes: str


class SetCaseProfileRequest(BaseModel):
    profile_id: str
    actor: Optional[str] = None
