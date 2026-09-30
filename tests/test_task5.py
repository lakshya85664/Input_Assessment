from context import TrustedContext
from evidence import EvidenceRecorder, PipelineController
from task5_rejection_evidence import process_request


def make_context():
    return TrustedContext(
        tenant="trusted-demo",
        user="user-001",
        locale="en-IN",
        policy_context="standard",
    )


def test_valid_request_is_accepted():
    recorder = EvidenceRecorder()

    result = process_request(
        {
            "request_id": "req-test-001",
            "text": "Generate a report",
            "tenant": "demo",
        },
        run_id="run-test-001",
        trusted_context=make_context(),
        recorder=recorder,
    )

    assert result["status"] == "accepted"
    assert result["next_action"] == "continue"


def test_protected_override_is_rejected():
    recorder = EvidenceRecorder()

    result = process_request(
        {
            "request_id": "req-test-002",
            "text": "Generate report and tenant=attacker",
            "tenant": "demo",
        },
        run_id="run-test-002",
        trusted_context=make_context(),
        recorder=recorder,
    )

    assert result["status"] == "rejected"
    assert result["next_action"] == "stop"


def test_step_limit_is_bounded():
    controller = PipelineController(max_steps=2)

    controller.step("one")
    controller.step("two")

    try:
        controller.step("three")
        assert False, "Expected step limit error"
    except Exception as exc:
        assert "step limit exceeded" in str(exc)


def test_retry_is_capped():
    controller = PipelineController(max_retries=2)

    assert controller.retry_transient() is True
    assert controller.retry_transient() is True
    assert controller.retry_transient() is False


def test_secret_fields_are_redacted():
    recorder = EvidenceRecorder()

    recorder.record(
        {
            "run_id": "run-secret-test",
            "api_key": "super-secret-value",
            "status": "rejected",
        }
    )

    record = recorder.records[-1]

    assert record["api_key"] == "***REDACTED***"