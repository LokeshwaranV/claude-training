"""Tests for Step 15 observability: retrieval latency, grounding failures,
and refusal-rate counters. Uses the OTel SDK's in-memory span
exporter/metric reader (no real exporter, no collector) via
`retrieval.telemetry.configure_for_testing()`.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import retrieval.telemetry as telemetry
from retrieval.answer import answer_query


def _metric_points(metrics_data, name: str):
    points = []
    for rm in metrics_data.resource_metrics:
        for sm in rm.scope_metrics:
            for metric in sm.metrics:
                if metric.name == name:
                    points.extend(metric.data.data_points)
    return points


def _counter_value(metrics_data, name: str) -> float:
    points = _metric_points(metrics_data, name)
    return sum(p.value for p in points)


def test_query_requests_and_grounding_failure_counters_on_refusal():
    span_exporter, metric_reader = telemetry.configure_for_testing()

    response = answer_query("this matches absolutely nothing in the corpus zzzqqxx")
    assert response.status.value == "refused"

    metrics_data = metric_reader.get_metrics_data()
    assert _counter_value(metrics_data, "query_requests_total") == 1
    assert _counter_value(metrics_data, "grounding_failures_total") == 1


def test_query_requests_counter_without_grounding_failure_on_success():
    span_exporter, metric_reader = telemetry.configure_for_testing()

    response = answer_query("What is the mechanism of action of semaglutide as a GLP-1 receptor agonist?")
    assert response.status.value == "answered"

    metrics_data = metric_reader.get_metrics_data()
    assert _counter_value(metrics_data, "query_requests_total") == 1
    assert _counter_value(metrics_data, "grounding_failures_total") == 0


def test_retrieval_latency_histogram_and_span_recorded():
    span_exporter, metric_reader = telemetry.configure_for_testing()

    answer_query("What is the mechanism of action of semaglutide as a GLP-1 receptor agonist?")

    metrics_data = metric_reader.get_metrics_data()
    latency_points = _metric_points(metrics_data, "retrieval_latency_seconds")
    assert len(latency_points) >= 1
    assert latency_points[0].count >= 1

    spans = span_exporter.get_finished_spans()
    span_names = [s.name for s in spans]
    assert "retrieval.retrieve" in span_names


def test_refusal_rate_derivable_from_counters_across_multiple_calls():
    span_exporter, metric_reader = telemetry.configure_for_testing()

    answer_query("this matches absolutely nothing in the corpus zzzqqxx")
    answer_query("What is the mechanism of action of semaglutide as a GLP-1 receptor agonist?")

    metrics_data = metric_reader.get_metrics_data()
    total = _counter_value(metrics_data, "query_requests_total")
    failures = _counter_value(metrics_data, "grounding_failures_total")
    assert total == 2
    assert failures == 1
    assert failures / total == 0.5
