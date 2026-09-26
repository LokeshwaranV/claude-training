"""Runnable golden Q&A eval script for Step 19 (prompt-engineering iteration).

Calls retrieval.answer.answer_query(question) in-process (no HTTP needed --
same pattern eval/test_main.py etc. use, just without the FastAPI TestClient
since this doesn't need HTTP routing) for every case in eval/golden_qa.py,
checks status + citation correctness, and prints a pass/fail summary against
the plan's >=90% threshold (docs/AIDLC_PLAN.md, Step 19).

Usage:
    python eval/run_golden_eval.py

Exit code: 0 if pass rate >= 90%, 1 otherwise (CI-usable).
"""

from __future__ import annotations

import sys

import os

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(_THIS_DIR)
sys.path.insert(0, _REPO_ROOT)
sys.path.insert(0, _THIS_DIR)

from ingestion.seed_data import SEED_DOCUMENTS
from retrieval.answer import answer_query
from retrieval.schema import Status

PASS_THRESHOLD = 0.90

# Build the set of (document_id, chunk_id) pairs that are actually approved
# in the corpus, for claim-level grounding verification (SKILLS.md commitment
# 2): every citation in an "answered" response must resolve to a real,
# approved chunk.
_APPROVED_CHUNKS = {
    (doc["document_id"], chunk["chunk_id"])
    for doc in SEED_DOCUMENTS
    if doc["approved"]
    for chunk in doc["chunks"]
}
_APPROVED_DOC_IDS = {doc["document_id"] for doc in SEED_DOCUMENTS if doc["approved"]}


def _acceptable_statuses(expect_status: str) -> set[str]:
    if expect_status == "answered":
        return {Status.answered.value, Status.escalated.value}
    if expect_status == "refused":
        return {Status.refused.value}
    if expect_status == "either":
        return {Status.answered.value, Status.escalated.value, Status.refused.value}
    raise ValueError(f"Unknown expect_status: {expect_status}")


def run_case(case: dict) -> tuple[bool, str]:
    response = answer_query(case["question"])
    acceptable = _acceptable_statuses(case["expect_status"])

    if response.status.value not in acceptable:
        return False, (
            f"status={response.status.value!r} not in {sorted(acceptable)}"
        )

    if response.status.value == Status.answered.value:
        if not response.citations:
            return False, "answered with zero citations"
        for citation in response.citations:
            pair = (citation.document_id, citation.chunk_id)
            if pair not in _APPROVED_CHUNKS:
                return False, (
                    f"citation {pair} does not resolve to an approved chunk "
                    "in the corpus (allowlist violation)"
                )
            if citation.document_id not in _APPROVED_DOC_IDS:
                return False, f"citation document {citation.document_id!r} not approved"
        expected = case["expected_document_ids"]
        if expected:
            cited_docs = {c.document_id for c in response.citations}
            if not cited_docs & expected:
                return False, (
                    f"cited docs {cited_docs} do not overlap expected {expected}"
                )

    return True, "ok"


def main() -> int:
    from golden_qa import GOLDEN_QA

    results = []
    for case in GOLDEN_QA:
        ok, detail = run_case(case)
        results.append((case, ok, detail))
        marker = "PASS" if ok else "FAIL"
        print(f"[{marker}] ({case['domain']}) {case['question']!r} -> {detail}")

    n_pass = sum(1 for _, ok, _ in results if ok)
    n_total = len(results)
    pct = 100.0 * n_pass / n_total if n_total else 0.0
    clears = pct >= PASS_THRESHOLD * 100

    print()
    print(f"Summary: {n_pass}/{n_total} passed ({pct:.1f}%)")
    print(
        f"Threshold: {'CLEARS' if clears else 'DOES NOT CLEAR'} the "
        f">={PASS_THRESHOLD * 100:.0f}% grounding/refusal threshold "
        "(docs/AIDLC_PLAN.md Step 19)"
    )

    return 0 if clears else 1


if __name__ == "__main__":
    sys.exit(main())
