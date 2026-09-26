# Observability and Load Testing (Steps 15-16)

Mirrors `docs/reviews/STEP_15_REVIEW.md` and `docs/reviews/STEP_16_REVIEW.md`.

## Step 15 — OpenTelemetry instrumentation

`retrieval/telemetry.py` adds, in the shared `retrieval/` layer (so both
HTTP and MCP entry points inherit it for free, per [[Architecture]]):

- a `retrieval.retrieve` span + latency histogram around
  `retrieval/engine.py::retrieve`
- `query_requests_total` / `grounding_failures_total` counters in
  `retrieval/answer.py::answer_query` — refusal rate =
  `grounding_failures_total / query_requests_total`

Exporter is env-var-selectable (`AGENTIC_RAG_OTEL_EXPORTER=otlp|console|none`),
defaulting to `otlp` targeting a Grafana-fed collector at
`http://localhost:4317`, and verified to no-op safely with no collector
running — this stays testable/runnable with zero external infra.

## Step 16 — load testing

Plan named k6/JMeter; k6 needed a new APT repo (system-level change) to
install here, so **locust** was substituted instead (pip-installable, no
system changes) — see `eval/LOADTEST.md`. `eval/loadtest.py` weights
`/query` heaviest, with grounded questions matched to real seed-doc
content plus a refusal-path question, so the load test exercises both of
[[Governing Rules]]' answered/refused paths.

Last observed run (30s, 10 users): 478 requests, 0% failures, p50 4ms /
p95 8ms, ~16.3 req/s overall (~11.9 req/s on `/query` alone).
`grounding_failures_total` was confirmed moving under load via the console
exporter, matching the refusal-question request count almost 1:1.

No live Grafana/collector is deployed — metrics were only ever checked via
the console exporter or in-memory test exporters. That's the next visible
gap if this build continues past Step 20's demo scope.

## Related

[[Architecture]] · [[Governing Rules]]
