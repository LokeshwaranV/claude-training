# Step 15 review — OpenTelemetry observability

Triage-only review (purely additive instrumentation over already-reviewed
Step 11/14 logic; `docs/DELEGATION.md` allows triage-alone for small diffs).

## Verdict: PASS (no notes)

Checked against all five `SKILLS.md` commitments — instrumentation is
purely observational, no control-flow change:

1. **Allowlist-only retrieval** — `retrieve()` in `retrieval/engine.py`
   unchanged; just wrapped in a `retrieval.retrieve` span + latency
   histogram.
2. **Claim-level grounding** — citation-building logic in
   `retrieval/answer.py` untouched.
3. **Structured output** — `QueryResponse`/`BrowseItem` construction
   untouched.
4. **Graceful refusal** — `grounding_failures_total` increments exactly on
   the existing sole refusal branch (`not results or results[0].score <
   MIN_RELEVANCE`); `query_requests_total` increments unconditionally at
   entry, so refusal rate = `grounding_failures_total /
   query_requests_total` is a valid ratio.
5. **Cross-domain browsing** — `browse_documents` untouched; `main.py`
   only adds a non-counting `http.browse` span.

**No live-collector dependency**: verified independently (not just backend's
self-report) — hit `/query` and `/browse` via `TestClient` with the default
`otlp` exporter and no collector listening; both returned 200, export
failures stay in the background exporter thread and never reach the
request path.

**No duplicated counting**: `mcp/server.py`'s tools call the same
`retrieval.answer.answer_query` / `retrieval.browse.browse_documents`
functions `main.py` calls, so counters increment once per logical call
regardless of entry point (HTTP vs MCP).

**Tests**: triage independently ran `python3 -m pytest eval/ -q` → 14
passed (10 pre-existing + 4 new in `eval/test_telemetry.py`).

**Frontend boundary**: no `/frontend` changes.

## Design choice

Targets **Grafana** via a standard OTLP-ingesting collector (SigNoz would
work identically — also OTLP). Exporter selectable via
`AGENTIC_RAG_OTEL_EXPORTER` env var: `otlp` (default,
`AGENTIC_RAG_OTEL_ENDPOINT` / `http://localhost:4317`), `console` (dev
stdout), `none` (no-op) — so the POC stays runnable/testable without any
external infra.

## Files

`retrieval/telemetry.py` (new), `eval/test_telemetry.py` (new, 4 tests),
`retrieval/engine.py`, `retrieval/answer.py`, `main.py` (spans/counters
added), `requirements.txt` (pinned `opentelemetry-api`/`sdk`/
`exporter-otlp`, already installed in the venv).
