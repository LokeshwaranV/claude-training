# Agentic RAG — Governing Rules

This file documents the non-negotiable rules that every agent (backend, frontend,
triage) and every generated response in this project must follow. It exists so
that any sub-agent, reviewer, or future contributor can check compliance without
re-reading the full case study.

## The commitments

1. **Allowlist-only retrieval** — the retriever must filter to sources tagged
   `approved: true` in the source registry *before* ranking. No document outside
   the allowlist may reach the generation step.
2. **Claim-level grounding** — every sentence of a generated answer must resolve
   to a citation (`document_id`, `chunk_id`) that exists in the allowlist. An
   answer with an unresolvable citation is invalid output, not a warning.
3. **Structured output** — responses conform to the fixed schema below. Free-text
   answers are a bug.
4. **Fail gracefully** — if retrieved evidence is insufficient or confidence is
   below threshold, return a `refusal` or `escalation` response instead of
   fabricating an answer.
5. **Cross-domain browsing** — users can browse/filter the allowlisted corpus by
   `source_type` (literature, patent, clinical_trial, internal_report) as a
   standalone exploration mode, separate from query/answer. Browsing is
   list-only (no generation, no citation synthesis) and still respects the
   allowlist filter.
6. **Open-research (ungrounded) mode is separate, opt-in, and visibly labeled** —
   the system may offer a second answering mode where the model answers from
   its own general knowledge beyond the allowlisted corpus. This mode:
   - is never triggered automatically as a fallback inside the grounded query
     path — commitment 4's refusal/escalation behavior always wins for
     grounded questions;
   - must use a distinct response shape (never `QueryResponse`) so it can
     never be confused with a citation-backed answer, and must never carry
     `citations` or the grounded `confidence`/`status` fields;
   - must be visibly and persistently labeled ungrounded/unverified in the UI
     every time its output is shown, not just on first use;
   - must be explicitly requested by the user (a mode switch), never the
     default view.

## Response schema

```json
{
  "answer": "string | null",
  "confidence": "high | medium | low",
  "citations": [
    {"document_id": "string", "chunk_id": "string", "source_type": "literature | patent | clinical_trial | internal_report"}
  ],
  "caveats": ["string"],
  "status": "answered | refused | escalated"
}
```

## Source registry expectations

Every ingested document must carry:
- `source_type` (literature / patent / clinical_trial / internal_report)
- `approved` (bool) — enforced allowlist flag
- `version` / `superseded_by` — to catch version drift
- `ingested_at`

## Agent responsibilities

- **backend agent**: ingestion, retrieval, grounding, schema enforcement, the
  Groq client and the open-research module.
- **frontend agent**: query UI, citation display, confidence indicators, the
  open-research mode switch and its persistent disclaimer.
- **P3-Triage-Agent**: read-only review of diffs against these commitments;
  reports pass/fail, never edits code directly.

See `docs/AIDLC_PLAN.md` for the full 20-step build plan and tool/model mapping.
