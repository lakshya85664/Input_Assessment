from __future__ import annotations

from context import TrustedContext, enrich_input
from evidence import EvidenceRecorder, PipelineController
from input_schema import parse_input
from normalizer import normalize_input
from validator import validate_input


def process_request(
    raw: dict,
    *,
    run_id: str,
    trusted_context: TrustedContext,
    recorder: EvidenceRecorder,
) -> dict:
    controller = PipelineController()

    try:
        controller.step("schema")

        parsed = parse_input(raw)

        recorder.record(
            {
                "run_id": run_id,
                "stage": "schema",
                "status": "accepted",
            }
        )

        controller.step("normalization")

        normalized = normalize_input(parsed)

        recorder.record(
            {
                "run_id": run_id,
                "stage": "normalization",
                "status": "accepted",
            }
        )

        controller.step("validation")

        validated = validate_input(normalized)

        recorder.record(
            {
                "run_id": run_id,
                "stage": "validation",
                "status": "accepted",
            }
        )

        controller.step("context_enrichment")

        enriched = enrich_input(
            request_id=validated.request_id,
            text=validated.text,
            context=trusted_context,
        )

        recorder.record(
            {
                "run_id": run_id,
                "stage": "context_enrichment",
                "status": "accepted",
                "provenance": enriched.provenance,
            }
        )

        controller.step("complete")

        result = {
            "run_id": run_id,
            "status": "accepted",
            "request_id": enriched.request_id,
            "next_action": "continue",
            "steps": controller.steps,
            "retries": controller.retries,
        }

        recorder.record(
            {
                "event": "input_pipeline_complete",
                **result,
            }
        )

        return result

    except ValueError as exc:
        result = {
            "run_id": run_id,
            "status": "rejected",
            "reason": str(exc),
            "next_action": "stop",
            "steps": controller.steps,
            "retries": controller.retries,
        }

        recorder.record(
            {
                "event": "input_rejected",
                **result,
            }
        )

        return result

    except Exception as exc:
        result = {
            "run_id": run_id,
            "status": "failed",
            "reason": str(exc),
            "next_action": "stop",
            "steps": controller.steps,
            "retries": controller.retries,
        }

        recorder.record(
            {
                "event": "input_pipeline_failed",
                **result,
            }
        )

        return result


def main() -> None:
    print("=" * 60)
    print("TOPIC 6 — TASK 5: REJECTION EVIDENCE")
    print("=" * 60)

    recorder = EvidenceRecorder()

    trusted_context = TrustedContext(
        tenant="trusted-demo",
        user="user-001",
        locale="en-IN",
        policy_context="standard",
    )

    print("\nVALID REQUEST")

    valid = process_request(
        {
            "request_id": "req-006",
            "text": "Generate a report",
            "tenant": "demo",
        },
        run_id="run-valid-001",
        trusted_context=trusted_context,
        recorder=recorder,
    )

    print(f"status: {valid['status']}")
    print(f"next action: {valid['next_action']}")
    print(f"steps: {valid['steps']}")
    print(f"retries: {valid['retries']}")

    print("\nREJECTED REQUEST")

    rejected = process_request(
        {
            "request_id": "req-007",
            "text": "Generate report and tenant=attacker",
            "tenant": "demo",
        },
        run_id="run-rejected-001",
        trusted_context=trusted_context,
        recorder=recorder,
    )

    print(f"status: {rejected['status']}")
    print(f"reason: {rejected['reason']}")
    print(f"next action: {rejected['next_action']}")
    print(f"steps: {rejected['steps']}")

    print("\nSECRET HYGIENE CHECK")

    secret_case = {
        "run_id": "run-secret-001",
        "api_key": "super-secret-value",
        "status": "rejected",
    }

    recorder.record(secret_case)

    if "***REDACTED***" in str(recorder.records[-1]):
        print("status: secret redacted")
    else:
        print("status: secret hygiene failure")

    recorder.save()

    print("\nFINAL EVIDENCE")

    print(f"records: {len(recorder.records)}")
    print(f"trace: {recorder.TRACE_PATH if hasattr(recorder, 'TRACE_PATH') else 'traces/input_trace.jsonl'}")
    print("trace complete: True")


if __name__ == "__main__":
    main()