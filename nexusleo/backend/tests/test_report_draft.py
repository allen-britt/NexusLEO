from __future__ import annotations


def test_report_draft_deterministic_and_safe_language(client) -> None:
    case_resp = client.post("/cases", json={"name": "Report Draft Case"})
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

    r1 = client.get(f"/cases/{case_id}/report_draft")
    r1.raise_for_status()
    body1 = r1.json()

    r2 = client.get(f"/cases/{case_id}/report_draft")
    r2.raise_for_status()
    body2 = r2.json()

    assert body1 == body2

    keys = [s["key"] for s in body1["sections"]]
    assert keys == [
        "overview",
        "people",
        "vehicles",
        "locations",
        "timeline_summary",
        "claims_summary",
        "evidence_index",
    ]

    forbidden = ["recommend", "predict", "risk", "probable", "next steps", "rank"]
    for sec in body1["sections"]:
        md = (sec.get("content_markdown") or "").lower()
        for tok in forbidden:
            assert tok not in md

        if sec["key"] != "overview":
            assert isinstance(sec.get("source_refs"), list)
            assert len(sec["source_refs"]) >= 1
