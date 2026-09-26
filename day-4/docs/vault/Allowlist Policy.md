# Allowlist Policy

## What "approved" means

Every ingested document (`ingestion/seed_data.py`) carries:

- `approved: bool` — the enforced allowlist flag. `retrieval/engine.py`
  filters to `approved: True` *before* any BM25/TF-IDF scoring happens —
  not after. `retrieval/browse.py::browse_documents()` applies the same
  filter for the browse path.
- `source_type` — one of `literature`, `patent`, `clinical_trial`,
  `internal_report`. Drives [[Governing Rules]]' cross-domain browsing
  commitment.
- `version` / `superseded_by` — version-drift tracking. Added to
  `retrieval/schema.py`'s `BrowseItem` and wired through `/browse` at Step
  12, after `code-review` caught it was missing from the original Step 11
  implementation (`docs/reviews/STEP_11_REVIEW.md`). Currently only
  `doc-ct-007` is marked superseded (by `doc-ct-003`); all others are
  `None`.
- `ingested_at` — per `SKILLS.md`'s source-registry expectations.

## Where the filter runs (single source of truth)

`retrieval/browse.py::browse_documents()` is the one implementation of the
allowlist+`source_type` filter — extracted at Step 14 out of what was
originally inlined in `main.py`'s `/browse` handler, so both the HTTP
endpoint and the MCP `browse` tool call the same function instead of two
copies that could drift apart.

## Why this matters for audit

Since claims may be legally challenged (per the case study), the source
trail (retrieval → chunk → citation) must be reconstructable after the
fact. Filtering before ranking, not after, means there is no code path
where an unapproved document's content can influence which chunks get
returned to generation — the audit story is "it was never in the
candidate set," not "it was excluded afterward."

## Related

[[Governing Rules]] · [[Architecture]]
