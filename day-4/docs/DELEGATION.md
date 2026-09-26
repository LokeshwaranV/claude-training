# Delegation policy (Step 7)

The main Claude Code session acts as orchestrator. It does not implement
backend/frontend/review work itself — it routes to the scoped sub-agent whose
file-scope (see each agent's Isolation section) matches the task, then waits
for that agent's result before continuing.

## Routing table

| Task touches...                                   | Route to             |
|-----------------------------------------------------|----------------------|
| `/ingestion`, `/retrieval`, `/mcp`, `/eval`, backend config | `backend` sub-agent |
| `/frontend`                                         | `frontend` sub-agent |
| Any diff, before merge/commit                       | `p3-triage-agent`    |
| Cross-cutting (e.g. `docs/`, `SKILLS.md`, `CLAUDE.md`, root scaffolding) | orchestrator itself |

## Sequencing rule

Every backend or frontend change is followed by a `p3-triage-agent` review
before it is committed. If triage returns `FAIL`, the orchestrator sends the
findings back to the originating sub-agent (backend or frontend) to fix, then
re-runs triage. Only commit on `PASS` or `PASS WITH NOTES` where the notes are
explicitly deferred (e.g. "revisit once Step 11 lands").

## Cross-agent requests

Sub-agents don't share memory (Step 6). If backend needs a frontend contract
change, or vice versa, it states the request explicitly; the orchestrator
relays it to the other sub-agent rather than letting agents talk directly or
assume shared context.

## Harness note

`.claude/agents/*.md` files are not auto-registered as `Agent`-tool
`subagent_type`s in this SDK-based environment (that registration is a Claude
Code CLI feature). Until/unless that changes, "route to X sub-agent" means:
launch a `general-purpose` agent, and its prompt must (a) tell it to read and
follow the target `.claude/agents/<name>.md` file as its role definition, and
(b) restate that file's isolation/scope rules explicitly, since a fresh agent
has no memory of this policy.
