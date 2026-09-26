"""OpenTelemetry observability setup."""

from typing import Optional
from opentelemetry import trace, metrics
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
import logging


class TelemetrySetup:
    """Setup OpenTelemetry for observability."""

    def __init__(
        self,
        service_name: str = "elation-chatbot",
        otel_endpoint: str = "http://localhost:4317",
        enabled: bool = True
    ):
        """Initialize telemetry."""
        self.service_name = service_name
        self.otel_endpoint = otel_endpoint
        self.enabled = enabled
        self.tracer: Optional[trace.Tracer] = None
        self.meter: Optional[metrics.Meter] = None

    def setup(self) -> None:
        """Setup OpenTelemetry exporters and instrumentors."""
        if not self.enabled:
            return

        try:
            # Setup trace exporter
            trace_exporter = OTLPSpanExporter(
                endpoint=self.otel_endpoint,
                insecure=True
            )
            trace_provider = TracerProvider()
            trace_provider.add_span_processor(BatchSpanProcessor(trace_exporter))
            trace.set_tracer_provider(trace_provider)
            self.tracer = trace.get_tracer(__name__)

            # Setup metric exporter
            metric_reader = PeriodicExportingMetricReader(
                OTLPMetricExporter(endpoint=self.otel_endpoint, insecure=True)
            )
            meter_provider = MeterProvider(metric_readers=[metric_reader])
            metrics.set_meter_provider(meter_provider)
            self.meter = metrics.get_meter(__name__)

            # Instrument libraries
            FastAPIInstrumentor().instrument()
            SQLAlchemyInstrumentor().instrument()
            RequestsInstrumentor().instrument()

            logging.info(f"OpenTelemetry setup complete: {self.otel_endpoint}")
        except Exception as e:
            logging.error(f"Failed to setup OpenTelemetry: {e}")
            self.enabled = False

    def create_span(self, name: str):
        """Create a new span."""
        if self.tracer:
            return self.tracer.start_as_current_span(name)
        else:
            # No-op context manager
            class NoOpSpan:
                def __enter__(self):
                    return self
                def __exit__(self, *args):
                    pass
            return NoOpSpan()

    def record_metric(
        self,
        name: str,
        value: float,
        unit: str = ""
    ) -> None:
        """Record a metric value."""
        if self.meter:
            counter = self.meter.create_counter(
                name=name,
                unit=unit,
                description=f"Counter for {name}"
            )
            counter.add(value)

    def set_gauge(
        self,
        name: str,
        value: float,
        unit: str = ""
    ) -> None:
        """Set a gauge metric."""
        if self.meter:
            gauge = self.meter.create_observable_gauge(
                name=name,
                unit=unit,
                description=f"Gauge for {name}"
            )


class MetricsCollector:
    """Collect application metrics."""

    def __init__(self, telemetry: TelemetrySetup):
        """Initialize metrics collector."""
        self.telemetry = telemetry
        self.api_calls_total = 0
        self.api_errors_total = 0
        self.response_times = []

    def record_api_call(
        self,
        endpoint: str,
        method: str,
        status_code: int,
        response_time_ms: float
    ) -> None:
        """Record an API call."""
        self.api_calls_total += 1

        if status_code >= 400:
            self.api_errors_total += 1

        self.response_times.append(response_time_ms)

        # Record with OpenTelemetry
        if self.telemetry.meter:
            self.telemetry.record_metric(
                f"api.calls.{method}_{status_code}",
                1,
                "count"
            )
            self.telemetry.record_metric(
                f"api.latency.{endpoint}",
                response_time_ms,
                "ms"
            )

    def record_llm_call(
        self,
        model: str,
        tokens_used: int,
        response_time_ms: float
    ) -> None:
        """Record an LLM API call."""
        if self.telemetry.meter:
            self.telemetry.record_metric(
                f"llm.calls.{model}",
                1,
                "count"
            )
            self.telemetry.record_metric(
                f"llm.tokens.{model}",
                tokens_used,
                "tokens"
            )
            self.telemetry.record_metric(
                f"llm.latency.{model}",
                response_time_ms,
                "ms"
            )

    def get_statistics(self) -> dict:
        """Get collected statistics."""
        avg_response_time = (
            sum(self.response_times) / len(self.response_times)
            if self.response_times else 0
        )

        return {
            "total_api_calls": self.api_calls_total,
            "total_errors": self.api_errors_total,
            "error_rate": (
                self.api_errors_total / self.api_calls_total * 100
                if self.api_calls_total > 0 else 0
            ),
            "avg_response_time_ms": avg_response_time,
            "max_response_time_ms": max(self.response_times) if self.response_times else 0,
            "min_response_time_ms": min(self.response_times) if self.response_times else 0
        }


class Logger:
    """Structured logging with OpenTelemetry."""

    def __init__(self, name: str):
        """Initialize logger."""
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

    def log_event(
        self,
        event_type: str,
        message: str,
        attributes: Optional[dict] = None
    ) -> None:
        """Log an event with attributes."""
        log_entry = {
            "event_type": event_type,
            "message": message,
            "attributes": attributes or {}
        }
        self.logger.info(log_entry)

    def log_error(
        self,
        error: Exception,
        context: Optional[dict] = None
    ) -> None:
        """Log an error with context."""
        self.logger.error(
            f"Error: {type(error).__name__}: {str(error)}",
            extra={"context": context or {}}
        )
