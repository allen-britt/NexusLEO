"""Root API router."""
from __future__ import annotations

from fastapi import APIRouter

from app.api.routes import cases, documents, ingest, claims

api_router = APIRouter()
api_router.include_router(cases.router, tags=["cases"])
api_router.include_router(documents.router, tags=["documents"])
api_router.include_router(ingest.router, tags=["ingest"])
api_router.include_router(claims.router, tags=["claims"])
