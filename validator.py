from __future__ import annotations

import re

from input_schema import InputRequest


class InputValidationError(ValueError):
    """Raised when an input violates an application-level policy."""


PROTECTED_FIELD_PATTERNS = (
    r"\btenant\s*=",
    r"\buser\s*=",
    r"\blocale\s*=",
    r"\brequest_id\s*=",
    r"\bpolicy_context\s*=",
)


def validate_input(request: InputRequest) -> InputRequest:
    """
    Validate an already schema-checked input request.

    This layer enforces application-level safety rules that are
    different from basic type/schema validation.
    """

    if not request.request_id.strip():
        raise InputValidationError("request_id must not be empty")

    if not request.tenant.strip():
        raise InputValidationError("tenant must not be empty")

    text = request.text.strip()

    if not text:
        raise InputValidationError("text must not be empty")

    if len(text) > 2000:
        raise InputValidationError(
            "text must be <= 2000 characters"
        )

    lowered = text.lower()

    for pattern in PROTECTED_FIELD_PATTERNS:
        if re.search(pattern, lowered):
            raise InputValidationError(
                "text attempts to override protected context"
            )

    return request