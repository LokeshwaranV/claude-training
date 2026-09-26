# Step 16 review — load testing

Triage-only review (new test tooling, no pipeline logic touched;
`docs/DELEGATION.md` allows triage-alone for small/tooling diffs).

## Verdict: PASS (no notes)

**Tool substitution**: `docs/AIDLC_PLAN.md` names k6/JMeter; k6 isn't
installed here and would require adding an external APT repo (system-level
change). User explicitly chose **locust** instead — pip-installable into
the project venv, no system changes. Documented in `eval/loadtest.py`'s
docstring and `eval/LOADTEST.md`.

**Coverage** — `eval/loadtest.py` exercises `/health`, `/browse`
(unfiltered + both valid `SourceType` filters), and `/query` weighted
heaviest (10 grounded + 3 refusal-path tasks vs 1-2 elsewhere), matching
Step 16's "against the query API" emphasis. The 4 grounded questions map
directly onto real seed-doc content in `ingestion/seed_data.py` (verified,
not topic-adjacent guessing); the refusal question ("CAR-T therapy for
pediatric leukemia") has no match in the 7-doc corpus and correctly
exercises the refusal path.

**Scope** — `git diff --stat` shows only `requirements.txt` (+`locust`)
and `.claude/state/backend.md` changed; `retrieval/`, `main.py`, `mcp/`
untouched. No `/frontend` touches. No secrets in new files.

**Numbers** — triage independently spot-ran a 5s/5-user load test against
the live local server (41 requests, 0 failures, p50 5ms/p95 17ms),
consistent in order of magnitude with the reported 30s/10-user run (478
requests, 0 failures, p50 4ms/p95 8ms, ~16.3 req/s overall, ~11.9 req/s on
`/query` alone).

**OTel sanity check** — `grounding_failures_total` (98) tracked the
refusal-question request count (97) almost 1:1 under load, consistent with
the script's task weights (refusal ≈ 11.5% of total weight) — confirms
Step 15's counters fire correctly under load, via console-exporter stdout
(no live Grafana/collector; not in scope for this step).

**Tests** — `pytest eval/ -q` → 14 passed, no regressions.

## Files

`eval/loadtest.py` (new), `eval/LOADTEST.md` (new — rerun instructions +
results table), `requirements.txt` (added `locust`).
