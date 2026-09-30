from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class TrustedContext(BaseModel):
    """
    Context supplied by the trusted application layer.

    These values must not be sourced from user-controlled text.
    """

    model_config = ConfigDict(extra="forbid")

    tenant: str = Field(min_length=1)
    user: str = Field(min_length=1)
    locale: str = Field(min_length=1)
    policy_context: str = Field(min_length=1)


class EnrichedInput(BaseModel):
    """
    Final input representation passed to downstream agent logic.
    """

    model_config = ConfigDict(extra="forbid")

    request_id: str = Field(min_length=1)
    text: str = Field(min_length=1, max_length=2000)

    tenant: str = Field(min_length=1)
    user: str = Field(min_length=1)
    locale: str = Field(min_length=1)
    policy_context: str = Field(min_length=1)

    provenance: dict[str, str]


def enrich_input(
    *,
    request_id: str,
    text: str,
    context: TrustedContext,
) -> EnrichedInput:
    """
    Combine validated user input with trusted application context.

    Protected context always comes from `TrustedContext`.
    """

    return EnrichedInput(
        request_id=request_id,
        text=text,
        tenant=context.tenant,
        user=context.user,
        locale=context.locale,
        policy_context=context.policy_context,
        provenance={
            "request_id": "application",
            "text": "user",
            "tenant": "trusted_context",
            "user": "trusted_context",
            "locale": "trusted_context",
            "policy_context": "trusted_context",
        },
    )