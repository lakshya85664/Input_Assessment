from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import Any


TRACE_PATH = Path("traces/input_trace.jsonl")

MAX_STEPS = 5
TIMEOUT_SECONDS = 2.0
MAX_RETRIES = 2

SECRET_KEYS = {
    "api_key",
    "token",
    "password",
    "secret",
    "authorization",
}


class StepLimitError(Exception):
    pass


class TimeoutError(Exception):
    pass


class TransientInputError(Exception):
    pass


class EvidenceRecorder:
    """
    Records structured evidence for accepted and rejected input.

    The recorder sanitizes known secret fields before writing evidence.
    """

    def __init__(self) -> None:
        self.records: list[dict[str, Any]] = []

    def sanitize(self, value: Any) -> Any:
        if isinstance(value, dict):
            return {
                key: "***REDACTED***"
                if key.lower() in SECRET_KEYS
                else self.sanitize(item)
                for key, item in value.items()
            }

        if isinstance(value, list):
            return [self.sanitize(item) for item in value]

        if isinstance(value, str):
            lowered = value.lower()

            for secret_name in SECRET_KEYS:
                if secret_name in lowered:
                    return re.sub(
                        rf"{secret_name}\s*[:=]\s*\S+",
                        f"{secret_name}=***REDACTED***",
                        value,
                        flags=re.IGNORECASE,
                    )

        return value

    def record(self, event: dict[str, Any]) -> None:
        safe_event = self.sanitize(event)
        self.records.append(safe_event)

    def save(self) -> None:
        TRACE_PATH.parent.mkdir(parents=True, exist_ok=True)

        with TRACE_PATH.open("w", encoding="utf-8") as file:
            for record in self.records:
                file.write(json.dumps(record) + "\n")


class PipelineController:
    """
    Provides bounded execution controls for the input pipeline.
    """

    def __init__(
        self,
        *,
        max_steps: int = MAX_STEPS,
        timeout_seconds: float = TIMEOUT_SECONDS,
        max_retries: int = MAX_RETRIES,
    ) -> None:
        self.max_steps = max_steps
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries

        self.steps = 0
        self.retries = 0
        self.started_at = time.monotonic()

    def step(self, name: str) -> None:
        elapsed = time.monotonic() - self.started_at

        if elapsed > self.timeout_seconds:
            raise TimeoutError(
                f"pipeline timeout exceeded during step: {name}"
            )

        if self.steps >= self.max_steps:
            raise StepLimitError(
                f"step limit exceeded at step: {name}"
            )

        self.steps += 1

    def retry_transient(self) -> bool:
        if self.retries >= self.max_retries:
            return False

        self.retries += 1
        return True