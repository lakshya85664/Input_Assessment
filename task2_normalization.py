from input_schema import parse_input
from normalizer import normalize_input


def main() -> None:
    print("=" * 60)
    print("TOPIC 6 — TASK 2: NORMALIZATION")
    print("=" * 60)

    print("\nHAPPY PATH")

    raw = {
        "request_id": "  req-002  ",
        "text": "   Plan    a    report    for this tenant   ",
        "tenant": "  demo  ",
    }

    parsed = parse_input(raw)
    normalized = normalize_input(parsed)

    print("status: normalized")
    print(f"request_id: '{normalized.request_id}'")
    print(f"text: '{normalized.text}'")
    print(f"tenant: '{normalized.tenant}'")

    print("\nREJECTION PATH")

    try:
        parse_input(
            {
                "request_id": "req-003",
                "text": "",
                "tenant": "demo",
            }
        )
    except ValueError as exc:
        print("status: rejected")
        print(f"reason: {exc}")


if __name__ == "__main__":
    main()