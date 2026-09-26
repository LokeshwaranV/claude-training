"""OpenTelemetry wiring for the Agentic RAG backend (Step 15, docs/AIDLC_PLAN.md).

Target backend: **Grafana** (via an OTel Collector -> Prometheus/Tempo/Loki, or
Grafana Cloud's OTLP endpoint) rather than SigNoz. Either is valid per Step 15;
Grafana is picked because it's the more common "bring your own collector"
target and needs nothing beyond a standard OTLP receiver, which keeps this
module infra-agnostic (SigNoz also ingests OTLP, so switching later is just a
matter of pointing OTEL_EXPORTER_OTLP_ENDPOINT at a different collector).

This is an offline POC: there is no LLM API key and no collector, Grafana, or
SigNoz instance running in this environment. Two things make that safe:

1. The OTLP exporter is configured with genuinely short timeouts/retries. If
   nothing is listening on the configured endpoint, span/metric export fails
   (or times out) in the background exporter thread and is swallowed by the
   SDK's BatchSpanProcessor / PeriodicExportingMetricReader — it does not
   raise into the request path and does not block app startup or requests.
   This was verified by starting the app with the OTLP exporter selected and
   no collector listening on localhost:4317, then hitting /query and /browse
   successfully (see .claude/state/backend.md for the verification note).
2. `AGENTIC_RAG_OTEL_EXPORTER` selects the exporter so this stays runnable and
   testable with zero external infra:
     - `otlp` (default) — OTLPSpanExporter/OTLPMetricExporter over gRPC,
       pointed at `AGENTIC_RAG_OTEL_ENDPOINT` (default
       `http://localhost:4317`, the standard local OTel Collector gRPC port).
       This is the production-intent path: point it at a collector that
       forwards to Grafana (Tempo/Mimir/Loki) or SigNoz.
     - `console` — ConsoleSpanExporter/ConsoleMetricExporter, dev-only, prints
       telemetry to stdout. Useful for manually eyeballing spans/metrics
       without any collector.
     - `none` — an in-process no-op: no SDK exporter/processor is registered
       at all, and OTel's own default no-op API is used. This is what
       `eval/` tests should NOT use directly (they use the SDK's
       `InMemorySpanExporter`/`InMemoryMetricReader` instead, wired via
       `configure_for_testing()` below) but it exists as the cheapest
       possible default for contexts that don't care about telemetry at all.

Instrumented signals (Step 15's three asks):
  - Retrieval latency: `retrieval_latency_seconds` histogram + a
    `retrieval.retrieve` span, both wrapping the allowlist-filter +
    BM25/TF-IDF scoring step in `retrieval/engine.py::retrieve()`.
  - Grounding failures: `grounding_failures_total` counter, incremented in
    `retrieval/answer.py::answer_query()` exactly on the refusal path (no
    allowlisted chunk cleared `MIN_RELEVANCE`) — confirmed by reading
    `answer.py`/`engine.py` that this is the sole "cannot ground" branch.
  - Refusal rate: derived from `grounding_failures_total` /
    `query_requests_total` (the latter incremented once per `answer_query()`
    call, refused or not) — both counters are exported so refusal rate is
    computable downstream (e.g. as a Grafana panel expression) without extra
    plumbing.

Both the HTTP path (`main.py`) and the MCP path (`mcp/server.py`) call
`retrieval.answer.answer_query` and `retrieval.browse.browse_documents`
directly (per the Step 14 shared-layer pattern) — so instrumenting those two
functions here means both entry points get identical, non-duplicated
telemetry for free. `main.py` adds one extra thin HTTP-level span around each
endpoint for request-level tracing (status code, route), per the task's
"instrument main.py's request handlers" instruction — it does not duplicate
the counters/histogram, which live only in the retrieval/answer layer.
"""

from __future__ import annotations

import os
import time
from contextlib import contextmanager

from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (
    ConsoleMetricExporter,
    InMemoryMetricReader,
    PeriodicExportingMetricReader,
)
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
    SimpleSpanProcessor,
)
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

_SERVICE_NAME = "agentic-rag-backend"
_DEFAULT_OTLP_ENDPOINT = "http://localhost:4317"

_tracer_provider: TracerProvider | None = None
_meter_provider: MeterProvider | None = None
_tracer = None
_meter = None
_retrieval_latency_histogram = None
_grounding_failures_counter = None
_query_requests_counter = None
_groq_synthesis_failures_counter = None
_open_research_requests_counter = None


def _build_resource() -> Resource:
    return Resource.create({"service.name": _SERVICE_NAME})


def _configure(
    exporter_kind: str,
    span_exporter=None,
    metric_reader=None,
) -> None:
    """(Re)configure global tracer/meter providers. Exporters may be passed
    directly (used by `configure_for_testing`); otherwise built from
    `exporter_kind` ("otlp" | "console" | "none")."""
    global _tracer_provider, _meter_provider, _tracer, _meter
    global _retrieval_latency_histogram, _grounding_failures_counter, _query_requests_counter
    global _groq_synthesis_failures_counter, _open_research_requests_counter

    resource = _build_resource()
    _tracer_provider = TracerProvider(resource=resource)
    metric_readers = []

    if span_exporter is not None or metric_reader is not None:
        if span_exporter is not None:
            _tracer_provider.add_span_processor(SimpleSpanProcessor(span_exporter))
        if metric_reader is not None:
            metric_readers = [metric_reader]
    elif exporter_kind == "otlp":
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
            OTLPSpanExporter,
        )
        from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import (
            OTLPMetricExporter,
        )

        endpoint = os.environ.get("AGENTIC_RAG_OTEL_ENDPOINT", _DEFAULT_OTLP_ENDPOINT)
        # Short timeout: if no collector is listening, exports fail fast in
        # the background export thread instead of hanging; failures are
        # swallowed by the SDK and never propagate into the request path.
        otlp_span_exporter = OTLPSpanExporter(endpoint=endpoint, timeout=2)
        otlp_metric_exporter = OTLPMetricExporter(endpoint=endpoint, timeout=2)
        _tracer_provider.add_span_processor(BatchSpanProcessor(otlp_span_exporter))
        metric_readers = [
            PeriodicExportingMetricReader(otlp_metric_exporter, export_interval_millis=15000)
        ]
    elif exporter_kind == "console":
        _tracer_provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
        metric_readers = [
            PeriodicExportingMetricReader(ConsoleMetricExporter(), export_interval_millis=15000)
        ]
    elif exporter_kind == "none":
        pass  # No processors/readers registered at all — pure no-op.
    else:
        raise ValueError(f"Unknown AGENTIC_RAG_OTEL_EXPORTER value: {exporter_kind!r}")

    _meter_provider = MeterProvider(resource=resource, metric_readers=metric_readers)

    # Note: we deliberately get the tracer/meter directly from our own local
    # provider objects rather than registering them as the process-global
    # provider via trace.set_tracer_provider()/metrics.set_meter_provider().
    # The OTel API only allows the global provider to be set once (later
    # calls are silently ignored with a warning), which would break
    # `configure_for_testing()`'s ability to rewire exporters per-test.
    _tracer = _tracer_provider.get_tracer("agentic_rag.retrieval")
    _meter = _meter_provider.get_meter("agentic_rag.retrieval")

    _retrieval_latency_histogram = _meter.create_histogram(
        name="retrieval_latency_seconds",
        description="Time spent in allowlist filtering + BM25/TF-IDF scoring",
        unit="s",
    )
    _grounding_failures_counter = _meter.create_counter(
        name="grounding_failures_total",
        description="Number of /query (or MCP query) calls that could not "
        "ground an answer (no allowlisted chunk cleared MIN_RELEVANCE)",
    )
    _query_requests_counter = _meter.create_counter(
        name="query_requests_total",
        description="Total answer_query() invocations (HTTP + MCP combined); "
        "grounding_failures_total / query_requests_total == refusal rate",
    )
    _groq_synthesis_failures_counter = _meter.create_counter(
        name="groq_synthesis_failures_total",
        description="Number of answer_query() calls where Groq synthesis "
        "was attempted but failed the post-hoc grounding check or timed "
        "out/errored, and were escalated instead of falling back silently",
    )
    _open_research_requests_counter = _meter.create_counter(
        name="open_research_requests_total",
        description="Total answer_open_research() invocations (ungrounded, "
        "opt-in open-research mode, SKILLS.md commitment 6)",
    )


def init_telemetry() -> None:
    """Idempotent setup, called once at import time by this module. Exporter
    selection via AGENTIC_RAG_OTEL_EXPORTER env var: 'otlp' (default,
    production-intent, points at AGENTIC_RAG_OTEL_ENDPOINT or
    http://localhost:4317), 'console' (dev, prints to stdout), or 'none'
    (pure no-op)."""
    exporter_kind = os.environ.get("AGENTIC_RAG_OTEL_EXPORTER", "otlp").lower()
    _configure(exporter_kind)


def configure_for_testing() -> tuple[InMemorySpanExporter, InMemoryMetricReader]:
    """Test-only helper: rewires the global providers to the OTel SDK's
    in-memory exporters, so `eval/` tests can assert on emitted spans/metrics
    without any real exporter or collector. Returns (span_exporter,
    metric_reader); call `metric_reader.get_metrics_data()` /
    `span_exporter.get_finished_spans()` after driving a request."""
    span_exporter = InMemorySpanExporter()
    metric_reader = InMemoryMetricReader()
    _configure("otlp", span_exporter=span_exporter, metric_reader=metric_reader)
    return span_exporter, metric_reader


@contextmanager
def retrieval_span(name: str = "retrieval.retrieve"):
    """Wraps a block with a span + records its wall-clock duration into the
    retrieval_latency_seconds histogram. Used around the allowlist-filter +
    BM25/TF-IDF scoring step in retrieval/engine.py::retrieve()."""
    start = time.perf_counter()
    with _tracer.start_as_current_span(name):
        try:
            yield
        finally:
            _retrieval_latency_histogram.record(time.perf_counter() - start)


def record_query_request() -> None:
    """Increment the total-queries counter. Call once per answer_query()
    invocation, regardless of outcome."""
    _query_requests_counter.add(1)


def record_grounding_failure() -> None:
    """Increment the grounding-failure counter. Call exactly on the refusal
    path in answer_query() (no allowlisted chunk cleared MIN_RELEVANCE)."""
    _grounding_failures_counter.add(1)


def record_groq_synthesis_failure() -> None:
    """Increment the Groq-synthesis-failure counter. Call exactly when a
    Groq-synthesized grounded answer fails the post-hoc grounding check or
    the API call itself errors/times out, and answer_query() escalates
    instead of falling back silently."""
    _groq_synthesis_failures_counter.add(1)


def record_open_research_request() -> None:
    """Increment the open-research-requests counter. Call once per
    answer_open_research() invocation."""
    _open_research_requests_counter.add(1)


@contextmanager
def http_span(name: str):
    """Thin request-level span for main.py's HTTP handlers. Does not
    duplicate the counters/histogram above, which live in the shared
    retrieval/answer layer both main.py and mcp/server.py call into."""
    with _tracer.start_as_current_span(name):
        yield


init_telemetry()
