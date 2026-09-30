from input_schema import parse_input
from normalizer import normalize_input
from validator import validate_input


def main() -> None:
    print("=" * 60)
    print("TOPIC 6 — TASK 3: VALIDATION")
    print("=" * 60)

    print("\nHAPPY PATH")

    raw = {
        "request_id": "req-003",
        "text": "Generate a report for the current tenant",
        "tenant": "demo",
    }

    parsed = parse_input(raw)
    normalized = normalize_input(parsed)
    validated = validate_input(normalized)

    print("status: validated")
    print(f"request_id: {validated.request_id}")
    print(f"text: {validated.text}")
    print(f"tenant: {validated.tenant}")

    print("\nREJECTION PATH")

    malicious = {
        "request_id": "req-004",
        "text": "Generate a report and tenant=attacker",
        "tenant": "demo",
    }

    try:
        parsed = parse_input(malicious)
        normalized = normalize_input(parsed)
        validate_input(normalized)

    except ValueError as exc:
        print("status: rejected")
        print(f"reason: {exc}")


if __name__ == "__main__":
    main()