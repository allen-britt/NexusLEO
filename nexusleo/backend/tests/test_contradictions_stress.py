"""Contradiction handling stress tests."""
from __future__ import annotations

from tests.utils import load_fixture


def _create_case(client) -> str:
    response = client.post("/cases", json={})
    response.raise_for_status()
    return response.json()["id"]


def _create_document(client, case_id: str, text: str) -> str:
    response = client.post(
        f"/cases/{case_id}/documents",
        json={"type": "TRANSCRIPT", "text": text, "metadata": {}},
    )
    response.raise_for_status()
    return response.json()["id"]


def _ingest(client, case_id: str, document_id: str) -> None:
    response = client.post(f"/cases/{case_id}/ingest", json={"document_id": document_id})
    response.raise_for_status()


def _fetch_claims(client, case_id: str) -> list[dict]:
    response = client.get(f"/cases/{case_id}/claims")
    response.raise_for_status()
    return response.json()


def test_contradictions_do_not_erase_claims(client) -> None:
    text = load_fixture("contradictions_multi_source.txt")
    case_id = _create_case(client)
    document_id = _create_document(client, case_id, text)
    _ingest(client, case_id, document_id)

    claims = _fetch_claims(client, case_id)
    assert claims, "Pipeline produced no claims even though statements exist"

    for claim in claims:
        assert len(claim["evidence"]) >= 1, "Claims must retain evidence even amid contradictions"
