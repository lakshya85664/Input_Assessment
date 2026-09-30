from input_schema import parse_input


def main() -> None:
    print("=" * 60)
    print("TOPIC 6 — TASK 1: INPUT SCHEMA")
    print("=" * 60)

    print("\nHAPPY PATH")

    valid_input = {
        "request_id": "req-001",
        "text": "Plan a report for this tenant",
        "tenant": "demo",
    }

    parsed = parse_input(valid_input)

    print("status: accepted")
    print(f"request_id: {parsed.request_id}")
    print(f"text: {parsed.text}")
    print(f"tenant: {parsed.tenant}")

    print("\nFAILURE PATH")

    invalid_input = {
        "request_id": "req-002",
        "text": "",
        "tenant": "demo",
    }

    try:
        parse_input(invalid_input)
    except ValueError as exc:
        print("status: rejected")
        print(f"reason: {exc}")


if __name__ == "__main__":
    main()