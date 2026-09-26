# Delegation Policy

Mirrors `docs/DELEGATION.md`.

The main Claude Code session acts as orchestrator — it doesn't implement
backend/frontend/review work itself, it routes:

| Task touches... | Route to |
|---|---|
| `/ingestion`, `/retrieval`, `/mcp`, `/eval`, backend config | backend sub-agent |
| `/frontend` | frontend sub-agent |
| Any diff, before merge/commit | p3-triage-agent |
| Cross-cutting (`docs/`, `SKILLS.md`, `CLAUDE.md`, root scaffolding) | orchestrator itself |

This vault (`docs/vault/`) is itself an example of the last row — Step 17
is cross-cutting documentation, so the orchestrator wrote it directly
rather than delegating to backend or frontend.

## Sequencing rule

Every backend/frontend change → triage review → only commit on PASS or
PASS WITH NOTES (where notes are explicitly deferred). FAIL sends findings
back to the originating sub-agent, then triage re-runs.

## Harness note

`.claude/agents/*.md` files aren't auto-registered as `Agent`-tool
`subagent_type`s in this SDK-based environment, so "route to X sub-agent"
in practice means: launch a `general-purpose` agent whose prompt tells it
to read and follow `.claude/agents/<name>.md` as its role, restating that
file's isolation rules explicitly (a fresh agent has no memory of this
policy otherwise).

## Related

[[Governing Rules]] · [[Context Trimming Policy]]
