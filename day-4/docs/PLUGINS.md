# Plugin/tool strategy (Step 10)

Step 10 of `docs/AIDLC_PLAN.md` is a decision step, not an implementation
step: pick which external plugins/skills this build reuses now, and confirm
what stays internal (built later as a custom MCP server in Step 14). Step 13
does the deeper mcpservers.org evaluation for infra-level MCP servers
(filesystem, Postgres, etc.) once the RAG engine (Step 11) needs them.

## External plugins/skills adopted now

- **`code-review` skill** — used per Step 12 on backend/frontend diffs,
  alongside (not instead of) the p3-triage-agent's SKILLS.md-specific check.
  `code-review` catches general correctness/simplification/efficiency
  issues; triage catches the four (plus browsing) domain commitments. Run
  both before merge on non-trivial diffs; triage alone suffices for
  small/docs-only changes.
- **`web-search`** (built into this environment) — reserved for later use
  discovering *candidate* sources during ingestion authoring/testing (e.g.
  checking a paper's metadata). It must never be used at query-time to
  answer a user's question directly — that would bypass the allowlist
  (commitment 1 in `SKILLS.md`). Query-time retrieval stays scoped to the
  ingested, allowlisted corpus only.

No other external plugins are adopted at this stage; revisit if Step 11
(RAG engine) or Step 15 (observability) surfaces a concrete gap (e.g. a
vector-store or tracing plugin).

## Internal tools — deferred to Step 14

Retrieval, grounding, and citation resolution stay as internal
FastAPI/Python functions (owned by the backend sub-agent) through Steps
11-13. They are **not** wrapped as MCP tools yet — that happens in Step 14,
once the RAG engine (Step 11) exists to wrap. Wrapping early would mean
building an MCP interface around a pipeline that doesn't exist, and
re-designing it once real retrieve/ground/cite behavior lands.

## Verification

- Step 10 is a decision doc, not code — nothing to test. Verification is
  that this doc's choices get referenced (not silently deviated from) when
  Steps 11-14 are implemented.
