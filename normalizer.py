from __future__ import annotations

import re

from input_schema import InputRequest


def normalize_text(value: str) -> str:
    """
    Normalize user-provided text without changing its basic meaning.

    Rules:
    - Strip leading/trailing whitespace.
    - Collapse repeated whitespace to a single space.
    """

    value = value.strip()
    return re.sub(r"\s+", " ", value)


def normalize_input(request: InputRequest) -> InputRequest:
    """
    Return a normalized copy of the validated input.

    Normalization happens only after schema validation.
    """

    return request.model_copy(
        update={
            "request_id": request.request_id.strip(),
            "text": normalize_text(request.text),
            "tenant": request.tenant.strip(),
        }
    )