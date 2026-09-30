# Topic 6 — Project Implementation Assessment: Input

## Project Overview
This project implements a controlled input layer for an AI agent architecture. The pipeline establishes a boundary between untrusted user input and downstream agent logic.

```text
Raw Input
  ↓
Schema
  ↓
Normalization
  ↓
Validation
  ↓
Context Enrichment
  ↓
Accepted Input / Rejection Evidence
```

## Objectives
- Define a strict input schema.
- Normalize incoming text deterministically.
- Apply application-level validation.
- Prevent user-controlled text from overriding protected context.
- Add trusted tenant, user, locale, request ID, and policy context.
- Preserve provenance.
- Produce structured evidence for accepted and rejected requests.
- Apply step, timeout, retry, validation, and secret-hygiene controls.

## Project Structure
```text
Input_Assessment/
├── input_schema.py
├── normalizer.py
├── validator.py
├── context.py
├── evidence.py
├── task1_input_schema.py
├── task2_normalization.py
├── task3_validation.py
├── task4_context_enrichment.py
├── task5_rejection_evidence.py
├── requirements.txt
├── .gitignore
├── tests/
│   ├── test_task1.py
│   ├── test_task2.py
│   ├── test_task3.py
│   ├── test_task4.py
│   └── test_task5.py
└── traces/
    └── input_trace.jsonl
```

## Setup
```cmd
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m pytest -q
```

## Task 1 — Input Schema
`InputRequest` defines request_id, text, and tenant. Values must be non-empty, text is limited to 2000 characters, and unknown fields are rejected.

Verified result: **5 passed**.

## Task 2 — Normalization
The normalization layer strips leading/trailing whitespace, collapses repeated whitespace, normalizes request ID and tenant, preserves the schema, and behaves deterministically.

Example:
```text
"   Plan    a    report    for this tenant   "
→ "Plan a report for this tenant"
```

Verified result: **5 passed**.

## Task 3 — Validation
Application-level validation runs after schema validation and normalization. It checks required values and rejects explicit attempts to override protected context.

Example:
```text
Generate a report and tenant=attacker
```

Result:
```text
status: rejected
reason: text attempts to override protected context
```

Verified result: **5 passed**.

## Task 4 — Context Enrichment
Trusted application context is added after validation. The enriched input contains tenant, user, locale, policy context, request ID, and provenance.

Provenance:
```text
request_id → application
text → user
tenant → trusted_context
user → trusted_context
locale → trusted_context
policy_context → trusted_context
```

The demonstration verified:
```text
user supplied tenant: demo
trusted tenant used: trusted-demo
status: protected context preserved
```

Verified result: **5 passed**.

## Task 5 — Rejection Evidence
The final pipeline records schema, normalization, validation, context enrichment, completion/rejection, run ID, next action, step count, retry count, and provenance.

Valid request:
```text
status: accepted
next action: continue
steps: 5
retries: 0
```

Rejected request:
```text
status: rejected
reason: text attempts to override protected context
next action: stop
steps: 3
```

Secret hygiene:
```text
status: secret redacted
```

Final evidence:
```text
records: 9
trace: traces/input_trace.jsonl
trace complete: True
```

Verified result: **5 passed**.

## Guardrails
- **Step limit:** PipelineController enforces a maximum number of steps.
- **Timeout:** elapsed execution time is checked against a configured bound.
- **Retry:** transient retries are capped.
- **Validation:** schema and application-level validation occur before enrichment.
- **Secret hygiene:** known sensitive fields are redacted before evidence is stored.
- **Protected context:** trusted tenant, user, locale, and policy context are separate from user text.
- **Provenance:** the source of enriched values remains visible.

## Final Verification
Individual task verification:
```text
Task 1: 5 passed
Task 2: 5 passed
Task 3: 5 passed
Task 4: 5 passed
Task 5: 5 passed
```

Task-specific total: **25 passed**.

Final full regression command:
```cmd
python -m pytest -q
```

Trace:
```text
traces/input_trace.jsonl
```

## Architecture Trade-offs
The implementation separates schema validation, normalization, application-level validation, and context enrichment. This creates a clearer trust boundary than putting all behavior into a single parser.

Trusted context is supplied independently of user text. This is more explicit than accepting all fields from one request dictionary, but it makes the security boundary and provenance visible.

The step, timeout, and retry controls are deliberately deterministic and lightweight for reproducibility. A production system could add distributed request tracking, stronger authorization, durable policy storage, rate limiting, and more advanced observability.

A local implementation avoids external APIs and keeps the assessment safe and repeatable.

## Reflection
This assessment helped me understand that input handling is a security and reliability boundary, not just a parsing step. An AI agent receives information from users, but not every part of that information should automatically be trusted as control information. Separating schema validation, normalization, validation, and context enrichment made that distinction much clearer.

The most important part for me was protected context. A user request can contain useful information, but fields such as tenant, user, locale, and policy context should come from trusted application sources. The provenance information makes this distinction visible and gives downstream components a way to understand where each value originated.

I also learned that rejection behavior should be observable. Instead of simply raising an exception and losing the context of what happened, the implementation records structured evidence containing the run ID, stage, status, reason, next action, and execution bounds. This is useful for debugging as well as safety verification.

Another useful aspect was secret hygiene. Even when the application is only producing local trace evidence, sensitive values should not be written into logs or traces. The redaction layer provides a simple but important protection.

The main trade-off was keeping the controls deterministic and lightweight. A production input gateway would need more advanced policy management, distributed tracing, authentication, rate limiting, and asynchronous processing. For this assessment, the simpler design makes the trust boundaries easy to understand and test.

Overall, this project reinforced the principle that reliable agent systems should establish a strong, observable boundary before untrusted input reaches reasoning or action layers.
