"""Entity ambiguity doctrine stress tests."""
from __future__ import annotations

from tests.utils import load_fixture
from app.models import ResolutionHypothesis, ResolutionStatus, Entity


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


def _setup_case_with_fixture(client, fixture_name: str) -> tuple[str, str]:
    text = load_fixture(fixture_name)
    case_id = _create_case(client)
    document_id = _create_document(client, case_id, text)
    _ingest(client, case_id, document_id)
    return case_id, document_id


def test_entity_ambiguity_cases(client, db_session_factory) -> None:
    # Case A: single-token PERSON mention should emit UNREVIEWED hypothesis.
    case_id, _ = _setup_case_with_fixture(client, "pronouns_and_aliases.txt")
    session = db_session_factory()
    hypotheses = (
        session.query(ResolutionHypothesis)
        .filter(ResolutionHypothesis.status == ResolutionStatus.UNREVIEWED)
        .all()
    )
    assert hypotheses, "Expected at least one UNREVIEWED hypothesis"
    assert any(
        h.features_json.get("reason") == "single_token_name" and h.features_json.get("name") == "John"
        for h in hypotheses
    ), "Missing single-token hypothesis marker for John"

    # Case B: Ryan and Rian stay distinct entities with hypotheses.
    case_id, _ = _setup_case_with_fixture(client, "ambiguity_ryan_rian.txt")
    session = db_session_factory()
    persons = (
        session.query(Entity)
        .filter(Entity.entity_type == "PERSON", Entity.canonical_name.in_(["Ryan", "Rian"]))
        .all()
    )
    names = {person.canonical_name for person in persons}
    assert {"Ryan", "Rian"} == names, "Ryan/Rian should remain separate entities"
    hypotheses = (
        session.query(ResolutionHypothesis)
        .filter(ResolutionHypothesis.status == ResolutionStatus.UNREVIEWED)
        .all()
    )
    assert hypotheses, "Ryan/Rian ingestion should create hypotheses"

    # Case C: identical canonical names (John Smith) remain documented with evidence.
    case_id, _ = _setup_case_with_fixture(client, "john_smith_two_people.txt")
    response = client.get(f"/cases/{case_id}/claims")
    response.raise_for_status()
    claims = response.json()
    assert claims, "Expected claims for John Smith scenario"
    for claim in claims:
        assert claim["evidence"], "Claims must retain evidence even under ambiguity"
    # NOTE: Doctrine v0.1 does not require splitting identical canonical names.
