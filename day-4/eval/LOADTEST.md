# Load testing (Step 16)

## Tool choice: locust instead of k6/JMeter

AIDLC_PLAN.md's Step 16 says "k6 or JMeter scripts against the query API."
k6 was not installed in this environment and installing it would require
adding an external APT repo (a system-level change outside this project's
scope). The user chose **locust** instead: pure-Python, installs with
`pip install locust` straight into the project venv, no system changes.
This is treated as an equivalent substitution within the same spirit of
the step (load-test the query API, report p50/p95 latency and
throughput), not a re-litigation of the tool choice.

## Script

`eval/loadtest.py` — a locust `HttpUser` that exercises:

- `GET /health`
- `GET /browse` (unfiltered, and filtered by `source_type=literature` /
  `source_type=clinical_trial`, both valid values from
  `retrieval/schema.py`'s `SourceType` enum)
- `POST /query` — weighted heaviest (task weight 10 for grounded
  questions + 3 for the refusal question, vs. 1-2 for `/health`/`/browse`)
  since Step 16 explicitly calls out the query API:
  - 4 realistic questions pulled from `ingestion/seed_data.py` topics
    (semaglutide mechanism, GLP-1 agonist cardiovascular trial outcomes,
    sustained-release formulation, dual GIP/GLP-1 vs single-target
    agonists) — all should retrieve grounded, `status=answered` responses.
  - 1 question with no match in the 7-doc seed corpus ("recommended
    dosage of a CAR-T therapy for pediatric leukemia") to exercise the
    refusal path (`status=refused`, increments `grounding_failures_total`).

## How to re-run

```bash
pip install -r requirements.txt   # includes locust
# with the backend running, e.g.:
#   AGENTIC_RAG_OTEL_EXPORTER=console uvicorn main:app --host 127.0.0.1 --port 8000
locust -f eval/loadtest.py --headless -u 10 -r 2 -t 30s \
    --host http://127.0.0.1:8000 --csv=/tmp/loadtest
```

Or drop `--headless` for the interactive web UI at http://localhost:8089.

## Last observed run (2026-09-19)

`locust -f eval/loadtest.py --headless -u 10 -r 2 -t 30s --host http://127.0.0.1:8000 --csv=/tmp/loadtest`
against a local uvicorn instance started with `AGENTIC_RAG_OTEL_EXPORTER=console`.

Aggregated across all endpoints: **478 requests, 0 failures (0.00% failure
rate)**, median (p50) **4 ms**, p95 **8 ms**, throughput **~16.3 req/s**.

Per-endpoint highlights (from the locust summary / `/tmp/loadtest_stats.csv`):

| Endpoint | Requests | Failures | p50 | p95 | req/s |
|---|---|---|---|---|---|
| `GET /health` | 27 | 0 | 3 ms | 6 ms | 0.93 |
| `GET /browse` (unfiltered) | 51 | 0 | 4 ms | 9 ms | 1.76 |
| `GET /browse?source_type=literature` | 29 | 0 | 4 ms | 6 ms | 1.00 |
| `GET /browse?source_type=clinical_trial` | 23 | 0 | 4 ms | 6 ms | 0.79 |
| `POST /query` (semaglutide mechanism) | 78 | 0 | 5 ms | 9 ms | 2.69 |
| `POST /query` (cardiovascular trial) | 51 | 0 | 5 ms | 6 ms | 1.76 |
| `POST /query` (sustained-release formulation) | 70 | 0 | 4 ms | 8 ms | 2.41 |
| `POST /query` (dual GIP/GLP-1) | 48 | 0 | 4 ms | 9 ms | 1.66 |
| `POST /query` (refusal question) | 97 | 0 | 5 ms | 10 ms | 3.34 |

All `/query` traffic combined: p50 ~4-5 ms, p95 ~6-10 ms, ~11.9 req/s
combined throughput, 0% failures.

### OTel sanity check (Step 15 instrumentation under load)

`/tmp/uvicorn.log` (the orchestrator's redirected uvicorn stdout, outside
this agent's repo scope but readable since it's not a repo-scope
violation) was grepped for the console-exporter metric dumps. Confirmed
both Step 15 signals moved during the load-test window: at the end of the
run, `query_requests_total` = **348** and `grounding_failures_total` =
**98** — the latter matching almost exactly the 97 refusal-question
requests actually sent (small residual timing skew between the metric
snapshot and the final locust tally), i.e. the refusal path is correctly
incrementing the grounding-failure counter and the histogram
(`retrieval_latency_seconds`) was recording non-zero counts/sums as well.
No live OTLP collector is running, so this was checked via the
`console` exporter's stdout JSON dumps, not a Grafana dashboard.
