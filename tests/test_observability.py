import json
import logging
import sys

import pytest
from fastapi.testclient import TestClient

from vouch.api.app import app
from vouch.observability import CORRELATION_HEADER, JsonFormatter

client = TestClient(app)


def request_log_lines(caplog: pytest.LogCaptureFixture) -> list[dict[str, object]]:
    formatter = JsonFormatter()
    return [
        json.loads(formatter.format(record))
        for record in caplog.records
        if record.name == "vouch.request"
    ]


def test_log_line_is_json_with_the_required_fields(caplog):
    caplog.set_level(logging.INFO)

    client.get("/profiles/7")

    line = request_log_lines(caplog)[-1]
    assert line["level"] == "info"
    assert line["message"] == "request finished"
    assert "timestamp" in line
    assert line["correlation_id"] not in ("", "-")


def test_given_correlation_id_is_used_in_logs_and_response(caplog):
    caplog.set_level(logging.INFO)

    response = client.get("/profiles/7", headers={CORRELATION_HEADER: "abc-123"})

    assert response.headers[CORRELATION_HEADER] == "abc-123"
    assert request_log_lines(caplog)[-1]["correlation_id"] == "abc-123"


def test_missing_correlation_id_is_generated():
    first = client.get("/health").headers[CORRELATION_HEADER]
    second = client.get("/health").headers[CORRELATION_HEADER]

    assert len(first) == 32
    assert first != second


def test_unsafe_correlation_id_is_replaced():
    response = client.get("/health", headers={CORRELATION_HEADER: "bad id\nfake log line"})

    assert response.headers[CORRELATION_HEADER] != "bad id\nfake log line"
    assert len(response.headers[CORRELATION_HEADER]) == 32


def test_request_log_includes_route_status_and_duration(caplog):
    caplog.set_level(logging.INFO)

    client.get("/profiles/7")

    line = request_log_lines(caplog)[-1]
    assert line["route"] == "/profiles/{user_id}"
    assert line["status"] == 200
    assert isinstance(line["duration_ms"], float)


def test_metrics_use_route_templates_not_raw_urls():
    client.get("/profiles/123456")
    client.get("/no-such-page/987654")

    text = client.get("/metrics").text

    assert 'route="/profiles/{user_id}"' in text
    assert 'route="unmatched"' in text
    assert "123456" not in text
    assert "987654" not in text


def test_health_checks_log_at_debug_only(caplog):
    caplog.set_level(logging.INFO)

    client.get("/health")

    assert request_log_lines(caplog) == []


def test_errors_include_the_stack_trace():
    try:
        raise ValueError("boom")
    except ValueError:
        record = logging.getLogger("test").makeRecord(
            "test", logging.ERROR, __file__, 1, "it failed", None, exc_info=sys.exc_info()
        )

    line = json.loads(JsonFormatter().format(record))
    assert line["level"] == "error"
    assert "ValueError: boom" in line["error"]
