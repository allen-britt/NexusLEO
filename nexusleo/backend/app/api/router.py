"""Root API router."""
from __future__ import annotations

from fastapi import APIRouter

from app.api.routes import cases, documents, ingest, claims

api_router = APIRouter()
api_router.include_router(cases.router, prefix="/cases", tags=["cases"])
api_router.include_router(documents.router, prefix="/cases", tags=["documents"])
api_router.include_router(ingest.router, prefix="/cases", tags=["ingest"])
api_router.include_router(claims.router, prefix="/cases", tags=["claims"])
