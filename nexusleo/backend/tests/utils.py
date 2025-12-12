"""Test utilities for fixtures."""
from __future__ import annotations

from pathlib import Path


def load_fixture(name: str) -> str:
    """Return the raw text for a fixture file under backend/tests/fixtures/."""
    base_dir = Path(__file__).resolve().parent / "fixtures"
    fixture_path = base_dir / name
    return fixture_path.read_text(encoding="utf-8")
