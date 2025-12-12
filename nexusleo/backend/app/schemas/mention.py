"""Mention schemas."""
from __future__ import annotations

from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class MentionOut(BaseModel):
    id: UUID
    document_id: UUID
    text: str
    start: int
    end: int
    speaker: Optional[str] = None
    timestamp: Optional[str] = None
    language: Optional[str] = None
    entity_type_guess: Optional[str] = None
