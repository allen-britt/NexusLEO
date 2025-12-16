from __future__ import annotations


def test_case_guidance_deterministic_and_safe_language(client) -> None:
    case_resp = client.post("/cases", json={"name": "Guidance Case"})
    case_resp.raise_for_status()
    case_id = case_resp.json()["id"]

    doc_resp = client.post(
        f"/cases/{case_id}/documents",
        json={
            "type": "TRANSCRIPT",
            "text": "A: John Smith met Jane Doe in Baltimore.\nB: John Smith met Jane Doe in Baltimore.",
            "metadata": {"source": "test"},
        },
    )
    doc_resp.raise_for_status()
    document_id = doc_resp.json()["id"]

    run_resp = client.post(f"/cases/{case_id}/run", json={"document_id": document_id, "actor": "test"})
    run_resp.raise_for_status()

    g1 = client.get(f"/cases/{case_id}/guidance")
    g1.raise_for_status()
    body1 = g1.json()

    g2 = client.get(f"/cases/{case_id}/guidance")
    g2.raise_for_status()
    body2 = g2.json()

    assert body1 == body2

    forbidden = ["recommend", "arrest", "charge", "probable", "should", "risk", "predict", "rank"]
    for item in body1["items"]:
        stmt = (item.get("statement") or "").lower()
        for tok in forbidden:
            assert tok not in stmt
