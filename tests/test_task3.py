import pytest

from input_schema import parse_input
from normalizer import normalize_input
from validator import InputValidationError, validate_input


def make_request(text: str):
    request = parse_input(
        {
            "request_id": "req-test",
            "text": text,
            "tenant": "demo",
        }
    )

    return normalize_input(request)


def test_valid_request_passes_validation():
    request = make_request("Generate a report")

    result = validate_input(request)

    assert result.text == "Generate a report"


def test_empty_text_is_rejected():
    with pytest.raises(ValueError):
        parse_input(
            {
                "request_id": "req-empty",
                "text": "",
                "tenant": "demo",
            }
        )


def test_protected_tenant_override_is_rejected():
    request = make_request(
        "Generate a report and tenant=attacker"
    )

    with pytest.raises(
        InputValidationError,
        match="protected context",
    ):
        validate_input(request)


def test_protected_user_override_is_rejected():
    request = make_request(
        "Generate a report for user=attacker"
    )

    with pytest.raises(
        InputValidationError,
        match="protected context",
    ):
        validate_input(request)


def test_normal_request_with_word_tenant_is_allowed():
    request = make_request(
        "Generate a report for the current tenant"
    )

    result = validate_input(request)

    assert result.tenant == "demo"