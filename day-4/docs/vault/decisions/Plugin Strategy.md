# Plugin Strategy (Step 10)

Mirrors `docs/PLUGINS.md`.

## Adopted now

- **`code-review` skill** — runs on backend/frontend diffs alongside (not
  instead of) [[Delegation Policy|p3-triage-agent's]] domain-specific check.
- **`web-search`** (built-in) — ingestion-authoring-time only (checking a
  candidate source's metadata). Never at query-time — that would bypass
  [[Allowlist Policy]].

## Deferred to Step 14

Retrieval/grounding/citation logic stayed as internal Python functions
through Steps 11-13, wrapped as MCP tools only once the RAG engine
actually existed to wrap (Step 14) — see [[MCP Server Strategy]].

## Related

[[MCP Server Strategy]] · [[Governing Rules]]
