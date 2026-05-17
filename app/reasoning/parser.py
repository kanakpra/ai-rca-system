import re
from datetime import datetime

from app.reasoning.severity import calculate_severity


def extract_important_logs(logs):

    lines = logs.split("\n")

    important = [
        line for line in lines
        if "ERROR" in line or "Exception" in line
    ]

    return important


def parse_log_events(log_lines):

    events = []

    for line in log_lines:

        match = re.match(
            r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) (.*)",
            line
        )

        if not match:
            continue

        timestamp_str = match.group(1)
        message = match.group(2)

        timestamp = datetime.strptime(
            timestamp_str,
            "%Y-%m-%d %H:%M:%S"
        )

        event = {
            "timestamp": timestamp,
            "raw": line,
            "message": message,
            "severity": calculate_severity(message)
        }

        events.append(event)

    return events