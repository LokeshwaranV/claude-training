# AIDLC POC template

Reusable scaffolding extracted from the Agentic RAG (pharma literature review)
build — Step 9 of `docs/AIDLC_PLAN.md`. Copy this directory's contents into a
new POC repo root and fill in the placeholders to reuse the same multi-agent
structure (isolated backend/frontend/triage sub-agents, delegation policy,
context trimming, hooks, structured-response schema pattern) for a different
domain.

## What's here

- `.claude/settings.json` — hooks (secret-scan on Bash, audit log on
  Edit/Write). Domain-agnostic as-is, copy verbatim.
- `.claude/agents/*.md.template` — backend/frontend/triage sub-agent
  definitions with the isolation rules that made Step 6 work. Fill in the
  `{{...}}` placeholders (domain, commitments, scope dirs).
- `.claude/state/README.md` — the summary+recent-turns state file format
  (Step 8's context-trimming policy) each sub-agent should keep for itself.
- `docs/DELEGATION.md.template` — the routing table + "triage before commit"
  rule (Step 7). Fill in the scope-to-agent mapping for the new project.
- `docs/CONTEXT_TRIMMING.md.template` — the trimming policy doc (Step 8),
  domain-agnostic apart from the project name.
- `docs/SKILLS.md.template` — shape for a project's own governing-rules doc:
  numbered non-negotiable commitments + a fixed response schema. Fill in the
  actual commitments and schema for the new domain.
- `schema_template.py` — the pydantic pattern used for structured,
  schema-enforced responses (enum-typed fields, a fixed top-level response
  model with a `status` discriminator for graceful refusal/escalation).

## How to use for a new POC

1. Copy this directory's contents into the new repo root (merge `.claude/`
   and `docs/` into the new repo's own).
2. Fill in every `{{PLACEHOLDER}}` — search for `{{` across the copied files.
3. Rename `*.md.template` → `*.md` (drop the `.template` suffix) and
   `schema_template.py` → wherever the new project's schema module lives.
4. Write the new project's own `SKILLS.md` from `docs/SKILLS.md.template`,
   then re-derive `.claude/agents/*.md` scopes and `docs/DELEGATION.md`'s
   routing table from it — the commitments should always come first, the
   agent scaffolding follows from them, not the other way round.
5. Create empty `.claude/state/<agent>.md` files per `.claude/state/README.md`
   and `docs/NEXT_SESSION_PROMPT.md` (see the parent project's copy for the
   shape) so a fresh session can resume without replaying git history.
