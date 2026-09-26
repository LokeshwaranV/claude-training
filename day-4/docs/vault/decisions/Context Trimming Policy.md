# Context Trimming Policy

Mirrors `docs/CONTEXT_TRIMMING.md`.

Each sub-agent's state file (`.claude/state/<agent>.md`) is split into a
`## Summary` (running, compressed, ~12-15% of context budget) and
`## Recent turns` (last 8-10 entries only — oldest fold into Summary, they
don't just get deleted). Applies per agent independently.

Exception: `.claude/state/triage.md` is append-only (a verdict history),
not summary+turns, since its audit value comes from keeping every entry.

`docs/NEXT_SESSION_PROMPT.md` is the equivalent trimming mechanism at the
*session* level (not per-agent) — it's the up-to-date resume prompt,
updated after every step, so a fresh session doesn't need to replay full
git history.

## Related

[[Delegation Policy]]
