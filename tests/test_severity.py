from app.reasoning.severity import calculate_severity


def test_timeout_severity():

    result = calculate_severity(
        "Database connection timeout"
    )

    assert result == 10


def test_401_severity():

    result = calculate_severity(
        "Unauthorized 401"
    )

    assert result == 9


def test_503_severity():

    result = calculate_severity(
        "503 Service Unavailable"
    )

    assert result == 6


def test_unknown_severity():

    result = calculate_severity(
        "Random message"
    )

    assert result == 1