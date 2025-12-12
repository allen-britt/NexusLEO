"""Claim invariants stress tests."""
from __future__ import annotations

from tests.utils import load_fixture


def _create_case(client) -> str:
    response = client.post("/cases", json={})
    response.raise_for_status()
    return response.json()["id"]


def _create_document(client, case_id: str, text: str) -> str:
    response = client.post(f"/cases/{case_id}/documents", json={"type": "TRANSCRIPT", "text": text, "metadata": {}})
    response.raise_for_status()
    return response.json()["id"]


def _ingest_document(client, case_id: str, document_id: str) -> None:
    response = client.post(f"/cases/{case_id}/ingest", json={"document_id": document_id})
    response.raise_for_status()


def _fetch_claims(client, case_id: str) -> list[dict]:
    response = client.get(f"/cases/{case_id}/claims")
    response.raise_for_status()
    return response.json()


def test_claim_invariants_with_corroboration(client) -> None:
    text = load_fixture("corroboration_two_speakers.txt")
    case_id = _create_case(client)
    document_id = _create_document(client, case_id, text)
    _ingest_document(client, case_id, document_id)

    claims = _fetch_claims(client, case_id)
    assert claims, "No claims were returned"

    assert any(claim["confidence"]["level"] == "HIGH" for claim in claims)
    for claim in claims:
        assert len(claim["evidence"]) >= 1, "Claim missing evidence links"
        assert claim.get("confidence") is not None, "Claim missing confidence block"
