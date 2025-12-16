"""FastAPI application entrypoint."""
from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.errors import ErrorToken

app = FastAPI(title="NexusLEO API")
app.include_router(api_router)


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=400, content={"detail": ErrorToken.INVALID_REQUEST.value})


@app.get("/healthz", response_model=dict[str, str])
def healthz() -> dict[str, str]:
    return {"status": "ok"}
