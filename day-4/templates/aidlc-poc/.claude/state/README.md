# Sub-agent state file format (Step 8)

Each sub-agent gets its own `.claude/state/<agent>.md`, split into two parts
so it never grows unbounded:

```
## Summary
<running summary of everything before the recent turns below,
kept to roughly 12-15% of the agent's context budget>

## Recent turns (latest 8-10 only)
- <turn N-9> ...
- ...
- <turn N> ...
```

- Anything older than the last 8-10 logged turns folds into `## Summary`
  (compress, don't append). If the summary grows past ~12-15% of context
  budget, compress harder — drop resolved details, keep decisions and open
  questions.
- A read-only reviewer agent (e.g. a triage agent) is the exception: keep its
  log append-only (one line per review: date, verdict, top issue) rather than
  summary+turns, since audit value comes from keeping every entry.
- Each agent trims only its own file — see the isolation rule in
  `.claude/agents/*.md.template`.

Create empty starting files for each sub-agent before first use, e.g.:

```
## Summary

(none yet)

## Recent turns
```
