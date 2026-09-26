# Step 12 — Review report for the Step 11 RAG engine

Per `docs/AIDLC_PLAN.md` Step 12 and `docs/PLUGINS.md`: the `code-review`
skill and the `p3-triage-agent` both reviewed the Step 11 diff (RAG engine).
This is the combined report artifact.

## Scope reviewed

Commit `f035b66` — Build the RAG engine end to end (Step 11):
`ingestion/seed_data.py`, `retrieval/engine.py`, `retrieval/answer.py`,
`main.py`, `eval/test_main.py`.

## p3-triage-agent — domain commitments (SKILLS.md)

| # | Commitment | Verdict | Note |
|---|---|---|---|
| 1 | Allowlist-only retrieval | PASS | `_approved_documents()` filters before `_approved_chunks()` builds the scored corpus; `/browse` filters inline too — no unapproved-document leak path found. |
| 2 | Claim-level grounding | PASS | Citations built exclusively from `top_chunks`, which come only from the allowlist-filtered `retrieve()` output; refusal branch returns `citations=[]`, never a non-null answer with empty/invalid citations. |
| 3 | Structured output | PASS | Both endpoints declare and return `retrieval/schema.py` models directly, no ad-hoc dicts. |
| 4 | Graceful failure | PASS, with a flagged gap | Refusal triggers correctly below `MIN_RELEVANCE=0.05`; confidence bands applied consistently. `escalated` status exists in the schema but is never triggered — flagged as a gap to revisit once a real corpus or multi-turn workflow exists. |
| 5 | Cross-domain browsing | PASS | `/browse` is pure list construction, no generation call, filters by `source_type` and enforces `approved`. |

Hygiene: no secrets, no PII in seed data. Triage independently re-ran
`pytest` itself (5 passed) rather than trusting the backend agent's
self-report.

## code-review skill — correctness/completeness

Two findings, both verified against the actual code before being accepted:

1. **`escalated` status is dead code** (`retrieval/answer.py:18`) — same gap
   triage flagged independently from a different angle (code-review framed
   it as "half-implemented commitment 4," triage framed it as "no cheap
   escalation trigger for this POC corpus"). Two independent reviews
   converging on the same gap raised its priority, but the underlying
   reasoning (no well-defined trigger in a 7-doc corpus) still holds, so
   this is **deferred, not fixed** — see "Deferred" below.
2. **Missing `superseded_by` field** (`ingestion/seed_data.py:20`) —
   SKILLS.md's "Source registry expectations" explicitly requires
   `version` / `superseded_by` on every ingested document to catch version
   drift, but the `Document` TypedDict and all seed entries omitted it;
   `doc-ct-007`'s relationship to `doc-ct-003` existed only as prose in a
   title string, not as structured data any code could act on.

## Gaps fixed in response to this review

- **`superseded_by` wired end to end** (fixed, this session, before this
  report):
  - `ingestion/seed_data.py` — added `superseded_by: str | None` to the
    `Document` TypedDict and to all 7 seed entries (`None` for current
    docs, `"doc-ct-003"` for `doc-ct-007`, the doc its own title says is
    superseded).
  - `retrieval/schema.py` — added `superseded_by: Optional[str] = None` to
    `BrowseItem` so the field is actually visible to API consumers, not
    just stored in the seed registry.
  - `main.py` — `/browse` now passes `superseded_by` through to the
    response.
  - Verified: `pytest eval/ -q` still 5 passed after the change (no
    existing test asserted on `BrowseItem`'s exact field set, so this was
    an additive, non-breaking change).

## Deferred (not fixed, with reasoning)

- **`escalated` status remains unimplemented.** Both reviews independently
  flagged this, but neither identified a cheap, well-defined trigger for a
  7-document POC corpus (e.g. conflicting evidence across `source_type`s
  requires at least two independently-sourced, contradicting claims about
  the same fact — the current seed corpus doesn't have that shape). Revisit
  when: (a) a real ingested corpus exists (Step 11 follow-on / production
  ingestion), or (b) a concrete conflicting-evidence test case is added to
  `eval/test_main.py` that the current pipeline actually fails on.

## Overall verdict

**PASS WITH NOTES** — the `superseded_by` gap is fixed and verified; the
`escalated` gap is explicitly deferred with a stated re-trigger condition,
not silently dropped.
