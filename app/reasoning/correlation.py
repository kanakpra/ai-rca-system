import re


def extract_services(events):

    services = set()

    for event in events:

        match = re.search(
            r"(Service\w+|PaymentService)",
            event["raw"]
        )

        if match:
            services.add(match.group())

    return list(services)


def determine_primary_issue(message):

    msg = message.lower()

    if "timeout" in msg:
        return "Database timeout"

    if "401" in msg or "unauthorized" in msg:
        return "Authentication failure"

    if "503" in msg:
        return "Service unavailable"

    if "nullpointerexception" in msg:
        return "Application exception"

    return "Unknown"


def correlate_incident(events):

    events.sort(key=lambda x: x["timestamp"])

    timeline = []

    secondary_effects = []

    probable_root_event = None

    for event in events:

        timeline.append({
            "time": event["timestamp"].strftime("%H:%M:%S"),
            "event": event["message"],
            "severity": event["severity"]
        })

        if (
            probable_root_event is None
            or event["severity"] > probable_root_event["severity"]
        ):
            probable_root_event = event

        if "503" in event["message"]:
            secondary_effects.append(
                "503 Service Unavailable"
            )

        if "NullPointerException" in event["message"]:
            secondary_effects.append(
                "NullPointerException"
            )

    primary_issue = determine_primary_issue(
        probable_root_event["message"]
    )

    return {
        "primary_issue": primary_issue,
        "primary_event": probable_root_event["message"],
        "primary_event_time":
            probable_root_event["timestamp"].strftime("%H:%M:%S"),
        "secondary_effects": list(set(secondary_effects)),
        "affected_services": extract_services(events),
        "timeline": timeline
    }