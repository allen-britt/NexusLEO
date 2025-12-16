"""Meta routes."""
from __future__ import annotations

import os

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.schemas.meta import VersionOut

router = APIRouter()


@router.get("/version", response_model=VersionOut)
def version(db: Session = Depends(get_db)) -> VersionOut:
    git_sha = os.getenv("GIT_SHA")

    schema_revision: str | None = None
    try:
        row = db.execute(text("SELECT version_num FROM alembic_version"))
        schema_revision = row.scalar()
    except Exception:
        schema_revision = None

    return VersionOut(
        service="NexusLEO",
        version="0.1.0-alpha",
        git_sha=git_sha,
        schema_revision=schema_revision,
    )
