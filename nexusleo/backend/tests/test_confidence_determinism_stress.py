"""Confidence determinism regression tests."""
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


def _ingest(client, case_id: str, document_id: str) -> dict:
    response = client.post(f"/cases/{case_id}/ingest", json={"document_id": document_id})
    response.raise_for_status()
    return response.json()


def _get_claims(client, case_id: str) -> list[dict]:
    response = client.get(f"/cases/{case_id}/claims")
    response.raise_for_status()
    return response.json()


def test_confidence_determinism(client) -> None:
    text = load_fixture("corroboration_two_speakers.txt")
    case_id = _create_case(client)
    document_id = _create_document(client, case_id, text)

    _ingest(client, case_id, document_id)
    claims_first = _get_claims(client, case_id)
    assert claims_first, "No claims returned after first ingest"

    snapshot: dict[tuple[str, str], dict] = {}
    required_keys = [
        "independent_evidence_count",
        "unique_speakers_count",
        "unique_documents_count",
        "has_single_token_person",
        "rule_claim_type",
    ]
    for claim in claims_first:
        key = (claim["predicate"], claim["text"])
        confidence = claim["confidence"]
        factors = confidence["factors_json"]
        for required_key in required_keys:
            assert required_key in factors, f"Missing confidence factor {required_key}"
        assert confidence["rubric_version"], "rubric_version must be present"
        snapshot[key] = confidence

    _ingest(client, case_id, document_id)
    claims_second = _get_claims(client, case_id)

    second_snapshot = {(claim["predicate"], claim["text"]): claim["confidence"] for claim in claims_second}
    assert set(snapshot.keys()) == set(second_snapshot.keys()), "Claim set changed after re-ingest"

    for key in snapshot:
        assert snapshot[key] == second_snapshot[key], f"Confidence mismatch for claim {key}"
