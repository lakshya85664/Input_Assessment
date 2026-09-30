from context import TrustedContext, enrich_input
from input_schema import parse_input
from normalizer import normalize_input
from validator import validate_input


def make_valid_request():
    request = parse_input(
        {
            "request_id": "req-005",
            "text": "Generate a report",
            "tenant": "user-supplied-tenant",
        }
    )

    request = normalize_input(request)
    return validate_input(request)


def make_trusted_context():
    return TrustedContext(
        tenant="trusted-tenant",
        user="user-001",
        locale="en-IN",
        policy_context="standard",
    )


def test_context_is_added():
    request = make_valid_request()
    context = make_trusted_context()

    result = enrich_input(
        request_id=request.request_id,
        text=request.text,
        context=context,
    )

    assert result.tenant == "trusted-tenant"
    assert result.user == "user-001"
    assert result.locale == "en-IN"
    assert result.policy_context == "standard"


def test_trusted_context_overrides_user_supplied_tenant():
    request = make_valid_request()
    context = make_trusted_context()

    result = enrich_input(
        request_id=request.request_id,
        text=request.text,
        context=context,
    )

    assert result.tenant != request.tenant
    assert result.tenant == "trusted-tenant"


def test_provenance_is_visible():
    request = make_valid_request()
    context = make_trusted_context()

    result = enrich_input(
        request_id=request.request_id,
        text=request.text,
        context=context,
    )

    assert result.provenance["text"] == "user"
    assert result.provenance["tenant"] == "trusted_context"
    assert result.provenance["user"] == "trusted_context"
    assert result.provenance["locale"] == "trusted_context"


def test_request_id_provenance_is_application_owned():
    request = make_valid_request()
    context = make_trusted_context()

    result = enrich_input(
        request_id=request.request_id,
        text=request.text,
        context=context,
    )

    assert result.provenance["request_id"] == "application"


def test_enriched_input_preserves_user_text():
    request = make_valid_request()
    context = make_trusted_context()

    result = enrich_input(
        request_id=request.request_id,
        text=request.text,
        context=context,
    )

    assert result.text == "Generate a report"