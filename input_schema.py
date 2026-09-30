from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class InputRequest(BaseModel):
    """
    Typed contract for an incoming agent request.

    Protected/context fields are represented explicitly so that later
    pipeline stages can distinguish trusted context from user content.
    """

    model_config = ConfigDict(extra="forbid")

    request_id: str = Field(min_length=1)
    text: str = Field(min_length=1, max_length=2000)
    tenant: str = Field(min_length=1)

    @field_validator("request_id", "text", "tenant")
    @classmethod
    def strip_required_strings(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("value must not be empty")

        return value


def parse_input(raw: dict[str, Any]) -> InputRequest:
    """
    Parse and validate the basic input schema.

    The function intentionally rejects unknown fields so that callers
    cannot silently inject unexpected control data into the input layer.
    """

    return InputRequest.model_validate(raw)