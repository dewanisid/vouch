"""Logging, metrics and tracing conventions. See docs/observability-conventions.md.

- Logs: one JSON object per line, with timestamp, level, message, logger,
  correlation_id and (inside a request) trace_id. Written to stdout and, when
  OTEL_EXPORTER_OTLP_ENDPOINT is set, sent to the OTel collector (then Loki).
- Traces: one per request, via OpenTelemetry, carrying the correlation ID.
- Metrics: request count and duration, labelled only with bounded values.
"""

import json
import logging
import os
import re
import sys
import time
import uuid
from collections.abc import Awaitable, Callable
from contextvars import ContextVar
from datetime import UTC, datetime
from typing import Any

from fastapi import FastAPI, Request, Response
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

CORRELATION_HEADER = "X-Correlation-ID"
# Accept a caller's ID only if it's short and plain, so it can't inject text into logs.
VALID_CORRELATION_ID = re.compile(r"[A-Za-z0-9._-]{1,64}")
# Requests that happen constantly (health checks, metric scrapes) log at DEBUG.
QUIET_PATHS = {"/health", "/metrics"}

correlation_id: ContextVar[str] = ContextVar("correlation_id", default="-")
logger = logging.getLogger("vouch.request")

# Labels are bounded: method, route *template* (never the raw URL or an ID), status.
REQUESTS = Counter("http_requests_total", "HTTP requests handled", ["method", "route", "status"])
DURATION = Histogram(
    "http_request_duration_seconds", "Time to handle an HTTP request", ["method", "route"]
)

# Attributes every LogRecord has; anything else was passed with `extra=` and is logged too.
_STANDARD_ATTRIBUTES = set(vars(logging.makeLogRecord({}))) | {
    "message",
    "asctime",
    "correlation_id",
    "trace_id",
    "taskName",
}


def _record_factory_with_ids(
    original: Callable[..., logging.LogRecord],
) -> Callable[..., logging.LogRecord]:
    """Stamp the correlation and trace IDs on each record when it's created."""

    def factory(*args: Any, **kwargs: Any) -> logging.LogRecord:
        record = original(*args, **kwargs)
        record.correlation_id = correlation_id.get()
        span_context = trace.get_current_span().get_span_context()
        record.trace_id = format(span_context.trace_id, "032x") if span_context.is_valid else None
        return record

    return factory


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        entry: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, UTC).isoformat(
                timespec="milliseconds"
            ),
            "level": record.levelname.lower(),
            "message": record.getMessage(),
            "logger": record.name,
            "correlation_id": getattr(record, "correlation_id", "-"),
        }
        trace_id = getattr(record, "trace_id", None)
        if trace_id:
            entry["trace_id"] = trace_id
        for key, value in vars(record).items():
            if key not in _STANDARD_ATTRIBUTES:
                entry[key] = value
        if record.exc_info:
            entry["error"] = self.formatException(record.exc_info)
        return json.dumps(entry, default=str)


def configure_logging() -> None:
    root = logging.getLogger()
    root.setLevel(os.environ.get("LOG_LEVEL", "INFO"))
    root.handlers.clear()

    stdout = logging.StreamHandler(sys.stdout)
    stdout.setFormatter(JsonFormatter())
    root.addHandler(stdout)

    if os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT"):
        provider = LoggerProvider(resource=_resource())
        provider.add_log_record_processor(BatchLogRecordProcessor(OTLPLogExporter()))
        otlp = LoggingHandler(logger_provider=provider)
        otlp.setFormatter(JsonFormatter())
        root.addHandler(otlp)

    # Uvicorn's loggers go through ours, so its lines are JSON too.
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        logging.getLogger(name).handlers.clear()
        logging.getLogger(name).propagate = True
    logging.getLogger("uvicorn.access").disabled = True  # we log each request ourselves

    if not getattr(logging, "_vouch_factory_installed", False):
        logging.setLogRecordFactory(_record_factory_with_ids(logging.getLogRecordFactory()))
        logging._vouch_factory_installed = True  # type: ignore[attr-defined]


def configure_tracing(app: FastAPI) -> None:
    provider = TracerProvider(resource=_resource())
    if os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT"):
        provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
    trace.set_tracer_provider(provider)
    FastAPIInstrumentor.instrument_app(app, excluded_urls="health,metrics")


def _resource() -> Resource:
    return Resource.create({"service.name": os.environ.get("OTEL_SERVICE_NAME", "vouch-api")})


def _route_template(request: Request) -> str:
    route = request.scope.get("route")
    return getattr(route, "path", "unmatched")


async def observe_request(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    """Middleware: correlation ID in, logs and metrics out."""
    given = request.headers.get(CORRELATION_HEADER, "")
    request_id = given if VALID_CORRELATION_ID.fullmatch(given) else uuid.uuid4().hex
    token = correlation_id.set(request_id)
    trace.get_current_span().set_attribute("correlation_id", request_id)

    started = time.perf_counter()
    status = 500
    try:
        response = await call_next(request)
        status = response.status_code
        response.headers[CORRELATION_HEADER] = request_id
        return response
    except Exception:
        logger.exception("request failed with an unhandled error")
        raise
    finally:
        seconds = time.perf_counter() - started
        route = _route_template(request)
        REQUESTS.labels(request.method, route, str(status)).inc()
        DURATION.labels(request.method, route).observe(seconds)
        level = logging.DEBUG if request.url.path in QUIET_PATHS else logging.INFO
        logger.log(
            level,
            "request finished",
            extra={
                "method": request.method,
                "route": route,
                "status": status,
                "duration_ms": round(seconds * 1000, 2),
            },
        )
        correlation_id.reset(token)


def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


def instrument(app: FastAPI) -> None:
    configure_logging()
    configure_tracing(app)
    app.middleware("http")(observe_request)
    app.add_api_route("/metrics", metrics, include_in_schema=False)
