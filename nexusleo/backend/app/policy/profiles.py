"""Static procedure profile packs.

Profiles are configuration packs, not database rows.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Profile:
    profile_id: str
    name: str
    scope: str
    jurisdiction: str
    version: str
    guidance_categories: list[str]
    notes: str


_PROCEDURE_CATEGORIES: list[str] = [
    "documentation_quality",
    "identity_handling",
    "timeline_consistency",
    "cross_source_alignment",
    "evidence_traceability",
    "data_gaps",
]


PROFILES: dict[str, Profile] = {
    "dmv-md": Profile(
        profile_id="dmv-md",
        name="DMV Procedure Profile (MD)",
        scope="DMV",
        jurisdiction="MD",
        version="0.1",
        guidance_categories=list(_PROCEDURE_CATEGORIES),
        notes="Neutral procedure profile for documentation-first workflows.",
    ),
    "dmv-dc": Profile(
        profile_id="dmv-dc",
        name="DMV Procedure Profile (DC)",
        scope="DMV",
        jurisdiction="DC",
        version="0.1",
        guidance_categories=list(_PROCEDURE_CATEGORIES),
        notes="Neutral procedure profile for documentation-first workflows.",
    ),
    "dmv-va": Profile(
        profile_id="dmv-va",
        name="DMV Procedure Profile (VA)",
        scope="DMV",
        jurisdiction="VA",
        version="0.1",
        guidance_categories=list(_PROCEDURE_CATEGORIES),
        notes="Neutral procedure profile for documentation-first workflows.",
    ),
}


def get_profile(profile_id: str) -> Profile | None:
    return PROFILES.get(profile_id)


def list_profiles() -> list[Profile]:
    return sorted(PROFILES.values(), key=lambda p: (p.jurisdiction, p.profile_id))
