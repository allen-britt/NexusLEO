"""Codes and call-types catalog endpoints."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid5, NAMESPACE_URL

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.core.db import get_db
from app.errors import ErrorToken
from app.models import AuditEvent, Case, CaseCodeSelection, CodeCatalog, CallTypeCatalog
from app.schemas import (
    CatalogSearchResponse,
    CaseCodeSelectionCreate,
    CaseCodeSelectionListResponse,
    CaseCodeSelectionOut,
    CaseCodeSelectionResponse,
    CodeSuggestionOut,
    CodeSuggestionResponse,
)

router = APIRouter()

_TOOL = "nexusleo.codes"
_TOOL_VERSION = "0.1.0"
_SUGGEST_VERSION = "0.1"


def _epoch() -> datetime:
    return datetime(1970, 1, 1, tzinfo=timezone.utc)


def _search_catalog(
    db: Session, model, jurisdiction: str, q: str, limit: int, offset: int
) -> CatalogSearchResponse:
    query = db.query(model).filter(model.jurisdiction == jurisdiction)
    if q:
        pattern = f"%{q}%"
        query = query.filter(
            or_(
                model.code.ilike(pattern),
                model.label.ilike(pattern),
                model.description.ilike(pattern),
            )
        )

    total = query.count()
    rows = (
        query.order_by(model.label.asc(), model.code.asc(), model.id.asc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return CatalogSearchResponse(
        generated_at=_epoch(),
        items=rows,
        total=total,
        limit=limit,
        offset=offset,
    )


def _selection_out(sel: CaseCodeSelection) -> CaseCodeSelectionOut:
    if sel.catalog_type == "CODE" and sel.code_catalog is not None:
        return CaseCodeSelectionOut(
            selection_id=sel.id,
            case_id=sel.case_id,
            catalog_type=sel.catalog_type,
            catalog_id=sel.code_catalog_id,
            code=sel.code_catalog.code,
            label=sel.code_catalog.label,
            system=sel.code_catalog.system,
            selected_by=sel.selected_by,
            selected_at=sel.selected_at,
            note=sel.note,
        )
    if sel.catalog_type == "CALL_TYPE" and sel.call_type_catalog is not None:
        return CaseCodeSelectionOut(
            selection_id=sel.id,
            case_id=sel.case_id,
            catalog_type=sel.catalog_type,
            catalog_id=sel.call_type_catalog_id,
            code=sel.call_type_catalog.code,
            label=sel.call_type_catalog.label,
            system=sel.call_type_catalog.system,
            selected_by=sel.selected_by,
            selected_at=sel.selected_at,
            note=sel.note,
        )
    raise HTTPException(status_code=400, detail=ErrorToken.INVALID_REQUEST.value)


def _suggestion_id(case_id: UUID, catalog_type: str, catalog_id: UUID) -> UUID:
    name = f"nexusleo:codes:{case_id}:{catalog_type}:{catalog_id}:{_SUGGEST_VERSION}"
    return uuid5(NAMESPACE_URL, name)


def _build_suggestions(
    db: Session, case: Case, state_ctx: dict, facts: dict
) -> list[CodeSuggestionOut]:
    jurisdiction = str(state_ctx.get("selected_state") or "").upper()
    if not jurisdiction:
        raise HTTPException(status_code=409, detail=ErrorToken.STATE_CONTEXT_REQUIRED.value)

    items: list[CodeSuggestionOut] = []

    def _find_code(predicate) -> Optional[CodeCatalog]:
        return (
            db.query(CodeCatalog)
            .filter(CodeCatalog.jurisdiction == jurisdiction)
            .filter(predicate)
            .order_by(CodeCatalog.label.asc(), CodeCatalog.code.asc(), CodeCatalog.id.asc())
            .first()
        )

    traffic = facts.get("traffic") if isinstance(facts, dict) else None
    speed = None
    if isinstance(traffic, dict):
        speed = traffic.get("speed_over_limit_mph")
    if isinstance(speed, (int, float)) and speed > 0:
        code_row = _find_code(or_(CodeCatalog.label.ilike("%speed%"), CodeCatalog.code.ilike("%SPD%")))
        if code_row:
            items.append(
                CodeSuggestionOut(
                    id=_suggestion_id(case.id, "CODE", code_row.id),
                    catalog_type="CODE",
                    catalog_id=code_row.id,
                    code=code_row.code,
                    label=code_row.label,
                    rationale_markdown="Observed speeding over posted limit.",
                    required_facts=["traffic.speed_over_limit_mph"],
                    missing_facts=[],
                )
            )

    person = facts.get("person") if isinstance(facts, dict) else None
    weapon_present = None
    if isinstance(person, dict):
        weapon_present = person.get("weapon_present")
    if weapon_present is True:
        code_row = _find_code(or_(CodeCatalog.label.ilike("%weapon%"), CodeCatalog.code.ilike("%WEAPON%")))
        if code_row:
            items.append(
                CodeSuggestionOut(
                    id=_suggestion_id(case.id, "CODE", code_row.id),
                    catalog_type="CODE",
                    catalog_id=code_row.id,
                    code=code_row.code,
                    label=code_row.label,
                    rationale_markdown="Weapon present according to observed facts.",
                    required_facts=["person.weapon_present"],
                    missing_facts=[],
                )
            )

    location = facts.get("location") if isinstance(facts, dict) else None
    school_zone = None
    if isinstance(location, dict):
        school_zone = location.get("school_zone")
    if school_zone is True:
        call_row = (
            db.query(CallTypeCatalog)
            .filter(CallTypeCatalog.jurisdiction == jurisdiction)
            .filter(or_(CallTypeCatalog.label.ilike("%school%"), CallTypeCatalog.code.ilike("%SCHOOL%")))
            .order_by(CallTypeCatalog.label.asc(), CallTypeCatalog.code.asc(), CallTypeCatalog.id.asc())
            .first()
        )
        if call_row:
            items.append(
                CodeSuggestionOut(
                    id=_suggestion_id(case.id, "CALL_TYPE", call_row.id),
                    catalog_type="CALL_TYPE",
                    catalog_id=call_row.id,
                    code=call_row.code,
                    label=call_row.label,
                    rationale_markdown="Incident flagged in school zone.",
                    required_facts=["location.school_zone"],
                    missing_facts=[],
                )
            )

    items.sort(key=lambda s: (s.catalog_type, s.label, s.code, s.id))
    return items


@router.get("/codes/search", response_model=CatalogSearchResponse)
def search_codes(
    jurisdiction: str = Query(...),
    q: str = Query(""),
    limit: int = Query(50, ge=0, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> CatalogSearchResponse:
    return _search_catalog(db, CodeCatalog, jurisdiction, q, limit, offset)


@router.get("/call-types/search", response_model=CatalogSearchResponse)
def search_call_types(
    jurisdiction: str = Query(...),
    q: str = Query(""),
    limit: int = Query(50, ge=0, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> CatalogSearchResponse:
    return _search_catalog(db, CallTypeCatalog, jurisdiction, q, limit, offset)


@router.post("/cases/{case_id}/codes/select", response_model=CaseCodeSelectionResponse)
def select_case_code(
    case_id: UUID,
    payload: CaseCodeSelectionCreate = Body(...),
    db: Session = Depends(get_db),
) -> CaseCodeSelectionResponse:
    case = db.query(Case).filter(Case.id == case_id).first()
    if case is None:
        raise HTTPException(status_code=404, detail=ErrorToken.CASE_NOT_FOUND.value)

    actor = payload.actor or "system"
    if payload.catalog_type == "CODE":
        catalog = db.get(CodeCatalog, payload.catalog_id)
        if catalog is None:
            raise HTTPException(status_code=404, detail=ErrorToken.CATALOG_NOT_FOUND.value)
        sel = CaseCodeSelection(
            case_id=case_id,
            catalog_type="CODE",
            code_catalog_id=payload.catalog_id,
            selected_by=actor,
            note=payload.note,
        )
    else:
        catalog = db.get(CallTypeCatalog, payload.catalog_id)
        if catalog is None:
            raise HTTPException(status_code=404, detail=ErrorToken.CATALOG_NOT_FOUND.value)
        sel = CaseCodeSelection(
            case_id=case_id,
            catalog_type="CALL_TYPE",
            call_type_catalog_id=payload.catalog_id,
            selected_by=actor,
            note=payload.note,
        )

    created = False
    try:
        db.add(sel)
        db.flush()
        created = True
    except IntegrityError:
        db.rollback()
        existing = (
            db.query(CaseCodeSelection)
            .options(joinedload(CaseCodeSelection.code_catalog), joinedload(CaseCodeSelection.call_type_catalog))
            .filter(
                CaseCodeSelection.case_id == case_id,
                CaseCodeSelection.catalog_type == payload.catalog_type,
                (
                    CaseCodeSelection.code_catalog_id == payload.catalog_id
                    if payload.catalog_type == "CODE"
                    else CaseCodeSelection.call_type_catalog_id == payload.catalog_id
                ),
            )
            .first()
        )
        if existing is None:
            raise HTTPException(status_code=400, detail=ErrorToken.INVALID_REQUEST.value)
        return CaseCodeSelectionResponse(selection=_selection_out(existing), created=False)

    db.flush()
    sel = (
        db.query(CaseCodeSelection)
        .options(joinedload(CaseCodeSelection.code_catalog), joinedload(CaseCodeSelection.call_type_catalog))
        .filter(CaseCodeSelection.id == sel.id)
        .one()
    )
    if created:
        audit = AuditEvent(
            case_id=case_id,
            actor=actor,
            action="code_selected",
            tool=_TOOL,
            tool_version=_TOOL_VERSION,
            input_refs_json={"case_id": str(case_id), "catalog_type": payload.catalog_type, "catalog_id": str(payload.catalog_id)},
            output_refs_json={"selection_id": str(sel.id)},
        )
        db.add(audit)

    db.commit()
    return CaseCodeSelectionResponse(selection=_selection_out(sel), created=created)


@router.get("/cases/{case_id}/codes", response_model=CaseCodeSelectionListResponse)
def list_case_codes(
    case_id: UUID,
    db: Session = Depends(get_db),
) -> CaseCodeSelectionListResponse:
    case = db.query(Case).filter(Case.id == case_id).first()
    if case is None:
        raise HTTPException(status_code=404, detail=ErrorToken.CASE_NOT_FOUND.value)

    rows = (
        db.query(CaseCodeSelection)
        .options(joinedload(CaseCodeSelection.code_catalog), joinedload(CaseCodeSelection.call_type_catalog))
        .filter(CaseCodeSelection.case_id == case_id)
        .order_by(
            CaseCodeSelection.selected_at.asc(),
            CaseCodeSelection.catalog_type.asc(),
            CaseCodeSelection.code_catalog_id.asc().nullsfirst(),
            CaseCodeSelection.call_type_catalog_id.asc().nullsfirst(),
            CaseCodeSelection.id.asc(),
        )
        .all()
    )
    items = [_selection_out(r) for r in rows]
    return CaseCodeSelectionListResponse(generated_at=_epoch(), items=items)


@router.get("/cases/{case_id}/codes/suggestions", response_model=CodeSuggestionResponse)
def suggest_case_codes(
    case_id: UUID,
    db: Session = Depends(get_db),
) -> CodeSuggestionResponse:
    case = db.query(Case).filter(Case.id == case_id).first()
    if case is None:
        raise HTTPException(status_code=404, detail=ErrorToken.CASE_NOT_FOUND.value)

    state_ctx = case.state_context_json
    if not isinstance(state_ctx, dict) or not state_ctx:
        raise HTTPException(status_code=409, detail=ErrorToken.STATE_CONTEXT_REQUIRED.value)

    facts = case.observed_facts_json if isinstance(case.observed_facts_json, dict) else {}
    items = _build_suggestions(db, case, state_ctx, facts)
    return CodeSuggestionResponse(generated_at=_epoch(), items=items)
