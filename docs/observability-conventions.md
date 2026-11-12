# Logging, metrics and tracing conventions

Every Vouch service follows these rules. The Python implementation is
[`src/vouch/observability.py`](../src/vouch/observability.py); calling
`instrument(app)` on a FastAPI app applies all of it.

| Signal | Answers | Stored in |
| --- | --- | --- |
| Metrics | *That* something is wrong, and how much | Prometheus (pulls `/metrics` every 15 s) |
| Traces | *Where* the time went | Tempo (via the OTel collector) |
| Logs | *Why* it happened | Loki (via the OTel collector), plus stdout |

Grafana shows all three.

## Correlation IDs

- Every request has a correlation ID. If the caller sends an `X-Correlation-ID`
  header, that value is used; otherwise the service creates one (32 hex characters).
- A caller's value is accepted only if it's 1–64 characters of letters, digits,
  `.`, `_` or `-`. Anything else is replaced, so the header can't inject fake
  lines or control characters into logs.
- The ID is returned in the response's `X-Correlation-ID` header, added to every
  log line written while handling the request, and set as the `correlation_id`
  attribute on the request's trace.
- When one service calls another (from Phase 3 on), it passes the same ID on.

To follow one request: search Loki for the correlation ID, then open its
`trace_id` in Tempo.

## Logs

One JSON object per line. Fields every line has:

| Field | Example |
| --- | --- |
| `timestamp` | `2026-11-12T19:06:31.309+00:00` (UTC, milliseconds) |
| `level` | `info` |
| `message` | `request finished`. A fixed phrase; the variable details go in fields, not in the sentence |
| `logger` | `vouch.request` |
| `correlation_id` | `demo-1794510391`, or `-` outside a request |
| `trace_id` | Present inside a request |

Add details as fields with `extra=`, not inside the message:

```python
logger.info("referral request sent", extra={"request_id": 41, "company_id": 3})
```

That way you can search for `company_id = 3` in Loki instead of matching text.

### Levels

| Level | Use it when | Example |
| --- | --- | --- |
| `debug` | Detail that's useful only while developing or chasing a bug. Off in normal runs | Health checks, metric scrapes, SQL parameters |
| `info` | Something normal and worth knowing happened | A request finished; a referral was sent; the seeder finished |
| `warning` | Something unexpected happened, but it was handled and the user wasn't affected | A retry succeeded; a deprecated field was used; a cache was unavailable and the database answered instead |
| `error` | An operation failed, and someone may need to look | A request returned 500; a message couldn't be processed. Include the stack trace (`logger.exception`) |
| `critical` | The service can't do its job at all | The database is unreachable at startup |

A rule of thumb: if a `warning` needs someone to act, it's really an `error`. If
an `error` happens every minute and nobody acts, fix the cause or lower the level.
Logs that cry wolf get ignored.

Set the level with the `LOG_LEVEL` environment variable (default `INFO`).

### Never log

Passwords, tokens, API keys, session cookies, full resumes, or any personal data
beyond an ID. Log `user_id=7`, not the user's email address. Logs are kept, copied
and read by many people. Treat them as public inside the team.

### Errors

Unhandled errors are logged at `error` with the full stack trace in an `error`
field, and the trace is marked as failed. A dedicated error-tracking tool, which
groups repeated errors and alerts on new ones, is a later decision (with an ADR).

### Rotation and retention

- Services write logs to **stdout**, never to files of their own (12-factor).
  Docker collects stdout.
- Docker rotates each container's log: at most **3 files of 10 MB**
  (`logging` options in `compose.yaml`). Without this, a busy container's log
  grows until the disk is full.
- Loki and Tempo keep their own copies. Tempo keeps traces for 72 hours locally.
  Loki retention gets set when we deploy (Phase 9).

## Metrics

Names follow Prometheus conventions: `snake_case`, the unit in the name, and
`_total` for counters.

| Metric | Type | Labels |
| --- | --- | --- |
| `http_requests_total` | Counter | `method`, `route`, `status` |
| `http_request_duration_seconds` | Histogram | `method`, `route` |

### Labels must be bounded

Every distinct combination of label values is a separate time series that
Prometheus stores and searches. A label whose values can grow without limit
(user IDs, raw URLs, email addresses, error messages) creates millions of series,
and Prometheus slows down or runs out of memory. This is called a
**cardinality explosion**.

- `route` is the route **template** (`/profiles/{user_id}`), never the real URL
  (`/profiles/7`). Requests that match no route are labelled `unmatched`, so
  random URLs from scanners can't create new series.
- Allowed label values come from a small, fixed set: HTTP methods, route
  templates, status codes, and later things like queue names.
- Per-user or per-request detail belongs in logs and traces, not metrics.

`tests/test_observability.py` checks that raw IDs never appear in `/metrics`.

## Traces

- OpenTelemetry instruments every FastAPI request. Spans are named after the
  route template.
- Health checks and metric scrapes aren't traced. They happen every few seconds
  and would bury the real requests.
- Settings come from standard OpenTelemetry environment variables:
  `OTEL_SERVICE_NAME` and `OTEL_EXPORTER_OTLP_ENDPOINT`. Without the endpoint
  (as in unit tests), traces and logs aren't sent anywhere.
