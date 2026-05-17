from app.reasoning.parser import (
    extract_important_logs,
    parse_log_events
)


def test_extract_important_logs():

    logs = """
    INFO Startup complete
    ERROR Database timeout
    INFO Healthcheck passed
    """

    result = extract_important_logs(logs)

    assert len(result) == 1
    assert "ERROR" in result[0]


def test_parse_log_events():

    logs = [
        "2026-04-26 10:01:10 ERROR ServiceDB timeout"
    ]

    events = parse_log_events(logs)

    assert len(events) == 1

    assert events[0]["severity"] == 10

    assert events[0]["message"] == (
        "ERROR ServiceDB timeout"
    )