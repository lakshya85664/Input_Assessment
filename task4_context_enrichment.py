from input_schema import parse_input
from normalizer import normalize_input
from validator import validate_input
from context import TrustedContext, enrich_input


def main() -> None:
    print("=" * 60)
    print("TOPIC 6 — TASK 4: CONTEXT ENRICHMENT")
    print("=" * 60)

    print("\nHAPPY PATH")

    raw = {
        "request_id": "req-005",
        "text": "Generate a report",
        "tenant": "demo",
    }

    parsed = parse_input(raw)
    normalized = normalize_input(parsed)
    validated = validate_input(normalized)

    trusted_context = TrustedContext(
        tenant="trusted-demo",
        user="user-001",
        locale="en-IN",
        policy_context="standard",
    )

    enriched = enrich_input(
        request_id=validated.request_id,
        text=validated.text,
        context=trusted_context,
    )

    print("status: enriched")
    print(f"request_id: {enriched.request_id}")
    print(f"text: {enriched.text}")
    print(f"tenant: {enriched.tenant}")
    print(f"user: {enriched.user}")
    print(f"locale: {enriched.locale}")
    print(f"policy_context: {enriched.policy_context}")
    print(f"provenance: {enriched.provenance}")

    print("\nPROTECTED CONTEXT CHECK")

    user_supplied_tenant = raw["tenant"]

    print(f"user supplied tenant: {user_supplied_tenant}")
    print(f"trusted tenant used: {enriched.tenant}")

    if user_supplied_tenant != enriched.tenant:
        print("status: protected context preserved")
    else:
        print("status: protected context collision")


if __name__ == "__main__":
    main()