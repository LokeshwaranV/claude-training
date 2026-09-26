# Governing Rules

Mirrors `SKILLS.md` (the source of truth — if this note and that file ever
disagree, `SKILLS.md` wins; update this note to match).

## The four-plus-one commitments

1. **Allowlist-only retrieval** — filter to `approved: true` *before*
   ranking. See [[Allowlist Policy]].
2. **Claim-level grounding** — every sentence resolves to a
   `(document_id, chunk_id)` citation that exists in the allowlist. An
   unresolvable citation is a bug, not a warning.
3. **Structured output** — fixed schema
   (`answer, confidence, citations[], caveats[], status`). Free text is a
   bug.
4. **Fail gracefully** — insufficient evidence or low confidence → `refused`
   or `escalated`, never a fabricated answer.
5. **Cross-domain browsing** — browse/filter by `source_type` as a
   standalone, list-only exploration mode; still allowlist-filtered.

## Who checks what

- **backend agent** — implements ingestion/retrieval/grounding/schema.
- **p3-triage-agent** — read-only, re-verifies every backend/frontend diff
  against these five points before merge; never edits code. See
  [[Delegation Policy]].
- **`code-review` skill** — general correctness/simplification pass,
  layered on top of triage for non-trivial diffs. See [[Plugin Strategy]].

## Known deferred gap

`escalated` status exists in the schema but has never been triggered —
there's no cheap, well-defined trigger for conflicting evidence in a 7-doc
POC corpus. Flagged independently at Step 11 and Step 12 review
(`docs/reviews/STEP_11_REVIEW.md`); revisit once a real corpus exists or a
concrete conflicting-evidence test case appears.

## Related

[[Architecture]] · [[Allowlist Policy]] · [[Delegation Policy]]
