"""Schemas for code/catalog smart stack."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


def _epoch() -> datetime:
    return datetime(1970, 1, 1, tzinfo=timezone.utc)


class CatalogSearchResultItem(BaseModel):
    id: UUID
    jurisdiction: str
    system: str
    code: str
    label: str
    description: Optional[str] = None
    tags_json: dict[str, Any] = Field(default_factory=dict)
    active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, extra="forbid")


class CatalogSearchResponse(BaseModel):
    generated_at: datetime = Field(default_factory=_epoch)
    items: list[CatalogSearchResultItem]
    total: int
    limit: int
    offset: int

    model_config = ConfigDict(extra="forbid")


class CaseCodeSelectionCreate(BaseModel):
    catalog_type: Literal["CODE", "CALL_TYPE"]
    catalog_id: UUID
    actor: Optional[str] = None
    note: Optional[str] = None

    model_config = ConfigDict(extra="forbid")


class CaseCodeSelectionOut(BaseModel):
    selection_id: UUID
    case_id: UUID
    catalog_type: Literal["CODE", "CALL_TYPE"]
    catalog_id: UUID
    code: str
    label: str
    system: str
    selected_by: str
    selected_at: datetime
    note: Optional[str] = None

    model_config = ConfigDict(extra="forbid")


class CaseCodeSelectionResponse(BaseModel):
    selection: CaseCodeSelectionOut
    created: bool

    model_config = ConfigDict(extra="forbid")


class CaseCodeSelectionListResponse(BaseModel):
    generated_at: datetime = Field(default_factory=_epoch)
    items: list[CaseCodeSelectionOut]

    model_config = ConfigDict(extra="forbid")


class CodeSuggestionOut(BaseModel):
    id: UUID
    catalog_type: Literal["CODE", "CALL_TYPE"]
    catalog_id: UUID
    code: str
    label: str
    rationale_markdown: str
    required_facts: list[str]
    missing_facts: list[str]

    model_config = ConfigDict(extra="forbid")


class CodeSuggestionResponse(BaseModel):
    generated_at: datetime = Field(default_factory=_epoch)
    items: list[CodeSuggestionOut]

    model_config = ConfigDict(extra="forbid")
