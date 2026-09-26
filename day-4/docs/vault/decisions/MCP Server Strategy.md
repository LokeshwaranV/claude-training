# MCP Server Strategy (Steps 13-14)

Mirrors `docs/MCP_EVALUATION.md` and the Step 14 build.

## Step 13 — infra servers evaluated, none adopted

| Candidate | Verdict | Why |
|---|---|---|
| filesystem MCP server | not adopted | no filesystem-based corpus exists — ingestion is in-memory `ingestion/seed_data.py` |
| Postgres MCP server | not adopted | no database exists at all — `retrieval/engine.py` is fully in-memory |
| web-search MCP server | not adopted | redundant with the built-in `web-search`, already scoped to authoring-time-only per [[Plugin Strategy]] |

All three are re-evaluatable, not permanently rejected — revisit if a real
corpus or persistence need appears.

## Step 14 — custom MCP server built

`mcp/server.py` exposes `query` and `browse` tools, wrapping
`retrieval/answer.py::answer_query` and
`retrieval/browse.py::browse_documents` directly — the same functions
`main.py`'s HTTP endpoints call, so nothing is duplicated between entry
points. See [[Architecture]].

## Related

[[Architecture]] · [[Plugin Strategy]] · [[Allowlist Policy]]
