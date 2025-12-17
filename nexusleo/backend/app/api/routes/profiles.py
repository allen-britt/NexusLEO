"""Profiles routes."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.errors import ErrorToken
from app.policy.profiles import get_profile, list_profiles
from app.schemas.profile import ProfileOut

router = APIRouter()


@router.get("/profiles", response_model=list[ProfileOut])
def get_profiles() -> list[ProfileOut]:
    return [ProfileOut(**p.__dict__) for p in list_profiles()]


@router.get("/profiles/{profile_id}", response_model=ProfileOut)
def get_profile_by_id(profile_id: str) -> ProfileOut:
    prof = get_profile(profile_id)
    if prof is None:
        raise HTTPException(status_code=404, detail=ErrorToken.PROFILE_NOT_FOUND.value)
    return ProfileOut(**prof.__dict__)
