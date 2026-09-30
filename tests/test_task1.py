import pytest

from input_schema import parse_input


def test_valid_input_is_accepted():
    result = parse_input(
        {
            "request_id": "req-001",
            "text": "Plan a report",
            "tenant": "demo",
        }
    )

    assert result.request_id == "req-001"
    assert result.text == "Plan a report"
    assert result.tenant == "demo"


def test_empty_text_is_rejected():
    with pytest.raises(ValueError):
        parse_input(
            {
                "request_id": "req-002",
                "text": "",
                "tenant": "demo",
            }
        )


def test_text_over_2000_characters_is_rejected():
    with pytest.raises(ValueError):
        parse_input(
            {
                "request_id": "req-003",
                "text": "x" * 2001,
                "tenant": "demo",
            }
        )


def test_missing_tenant_is_rejected():
    with pytest.raises(ValueError):
        parse_input(
            {
                "request_id": "req-004",
                "text": "Plan a report",
            }
        )


def test_unknown_fields_are_rejected():
    with pytest.raises(ValueError):
        parse_input(
            {
                "request_id": "req-005",
                "text": "Plan a report",
                "tenant": "demo",
                "unexpected_control": "should not be accepted",
            }
        )