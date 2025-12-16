"""Meta schemas."""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class VersionOut(BaseModel):
    service: str
    version: str
    git_sha: Optional[str] = None
    schema_revision: Optional[str] = None
