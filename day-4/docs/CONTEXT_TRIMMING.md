# Context trimming policy (Step 8)

Each sub-agent's isolated state file (`.claude/state/<agent>.md`, see Step 6)
is split into two parts so it never grows unbounded:

```
## Summary
<running summary of everything before the recent turns below,
kept to roughly 12-15% of the agent's context budget>

## Recent turns (latest 8-10 only)
- <turn N-9> ...
- ...
- <turn N> ...
```

## Rule

- Anything older than the last 8-10 logged turns gets folded into `## Summary`
  — compress, don't append. The summary should stay near 12-15% of the
  agent's total context budget; if it grows past that, compress harder
  (drop resolved details, keep decisions and open questions).
- `## Recent turns` never exceeds 8-10 entries — oldest entries roll off into
  the summary as new ones are added, they are not just deleted.
- This applies per agent independently (backend, frontend, triage) — each
  agent trims only its own file, per the isolation rule in Step 6.
- The triage agent's log (`.claude/state/triage.md`) is an exception: it's an
  append-only verdict history (one line per review), not a summary+turns
  file, since it's already compact and audit value comes from keeping every
  entry.

## Continuation prompt

`docs/NEXT_SESSION_PROMPT.md` holds the up-to-date prompt for resuming this
project in a fresh session. Update it after finishing each step so a new
session can pick up without re-deriving context from scratch.
