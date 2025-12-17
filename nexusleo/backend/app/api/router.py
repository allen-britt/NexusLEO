"""Root API router."""
from __future__ import annotations

from fastapi import APIRouter

from app.api.routes import cases, documents, ingest, claims, meta, demo, users, shifts, codes

api_router = APIRouter()
api_router.include_router(meta.router, tags=["meta"])
api_router.include_router(demo.router, tags=["demo"])
api_router.include_router(users.router, tags=["users"])
api_router.include_router(shifts.router, tags=["shifts"])
api_router.include_router(cases.router, tags=["cases"])
api_router.include_router(documents.router, tags=["documents"])
api_router.include_router(ingest.router, tags=["ingest"])
api_router.include_router(claims.router, tags=["claims"])
api_router.include_router(codes.router, tags=["codes"])
