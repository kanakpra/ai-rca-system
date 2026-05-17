def calculate_severity(message):

    msg = message.lower()

    if "timeout" in msg:
        return 10

    if "401" in msg or "unauthorized" in msg:
        return 9

    if "503" in msg:
        return 6

    if "nullpointerexception" in msg:
        return 4

    return 1