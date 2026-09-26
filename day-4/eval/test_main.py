"""Basic unit tests for the FastAPI app (main.py) and retrieval/schema.py.

Run with: pytest eval/
"""

from fastapi.testclient import TestClient

from main import app
from retrieval.schema import Status

client = TestClient(app)


def test_health_returns_200_and_ok_status():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_browse_returns_only_approved_items_for_requested_source_type():
    response = client.get("/browse", params={"source_type": "clinical_trial"})
    assert response.status_code == 200
    items = response.json()
    assert len(items) >= 1
    for item in items:
        assert item["source_type"] == "clinical_trial"
        assert item["approved"] is True
    # doc-ct-007 is an unapproved clinical_trial doc and must never appear.
    assert all(item["document_id"] != "doc-ct-007" for item in items)


def test_browse_without_filter_excludes_unapproved_docs():
    response = client.get("/browse")
    assert response.status_code == 200
    items = response.json()
    assert all(item["approved"] is True for item in items)
    unapproved_ids = {"doc-lit-005", "doc-pat-006", "doc-ct-007"}
    assert all(item["document_id"] not in unapproved_ids for item in items)


def test_query_with_allowlisted_match_answers_with_citations():
    response = client.post(
        "/query", params={"question": "What is the mechanism of action of semaglutide as a GLP-1 receptor agonist?"}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == Status.answered.value
    assert body["answer"]
    assert len(body["citations"]) >= 1
    for citation in body["citations"]:
        assert citation["document_id"]
        assert citation["chunk_id"]
    assert body["confidence"] in {"high", "medium", "low"}


def test_query_with_no_allowlisted_match_refuses():
    response = client.post(
        "/query", params={"question": "What is the recommended dosage for treating unrelated pediatric asthma inhalers?"}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == Status.refused.value
    assert body["answer"] is None
    assert body["citations"] == []
    assert body["caveats"]
