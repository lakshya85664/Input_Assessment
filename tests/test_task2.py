import pytest

from input_schema import parse_input
from normalizer import normalize_input


def test_normalization_strips_outer_whitespace():
    request = parse_input(
        {
            "request_id": "  req-001  ",
            "text": "  Plan a report  ",
            "tenant": "  demo  ",
        }
    )

    result = normalize_input(request)

    assert result.request_id == "req-001"
    assert result.text == "Plan a report"
    assert result.tenant == "demo"


def test_normalization_collapses_repeated_whitespace():
    request = parse_input(
        {
            "request_id": "req-002",
            "text": "Plan    a    report",
            "tenant": "demo",
        }
    )

    result = normalize_input(request)

    assert result.text == "Plan a report"


def test_normalization_is_deterministic():
    request = parse_input(
        {
            "request_id": "req-003",
            "text": "  Plan   a report  ",
            "tenant": "demo",
        }
    )

    first = normalize_input(request)
    second = normalize_input(request)

    assert first == second


def test_invalid_input_is_rejected_before_normalization():
    with pytest.raises(ValueError):
        parse_input(
            {
                "request_id": "req-004",
                "text": "",
                "tenant": "demo",
            }
        )


def test_normalization_does_not_add_fields():
    request = parse_input(
        {
            "request_id": "req-005",
            "text": "Plan a report",
            "tenant": "demo",
        }
    )

    result = normalize_input(request)

    assert result.model_dump().keys() == request.model_dump().keys()