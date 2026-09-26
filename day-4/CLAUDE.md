# Agentic RAG — Pharma Literature Review & Drug-Discovery Intelligence

AIDLC build (see `docs/AIDLC_PLAN.md` for the full 20-step plan). Governing
rules for all agents and generated code live in `SKILLS.md` — read it before
touching `/ingestion`, `/retrieval`, `/mcp`, or `/eval`.

## Layout

- `main.py`, `retrieval/` — Python/FastAPI backend (ingestion, retrieval, grounding, schema)
- `frontend/` — Next.js UI (query, browse, citations)
- `.claude/agents/backend.md`, `.claude/agents/frontend.md` — scoped sub-agents
- `docs/AIDLC_PLAN.md` — step-by-step plan and tool/model mapping

## Non-negotiables

Allowlist-only retrieval, claim-level grounding, fixed response schema, graceful
refusal/escalation, cross-domain browsing by `source_type`. Full detail in
`SKILLS.md`.
