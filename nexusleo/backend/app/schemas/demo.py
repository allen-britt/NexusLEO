"""Demo helper schemas."""
from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel


class DemoSeedOut(BaseModel):
    case_id: UUID
    document_id: UUID
