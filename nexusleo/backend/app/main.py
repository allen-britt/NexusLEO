"""FastAPI application entrypoint."""
from __future__ import annotations

from fastapi import FastAPI

from app.api.router import api_router

app = FastAPI(title="NexusLEO API")
app.include_router(api_router)


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}
