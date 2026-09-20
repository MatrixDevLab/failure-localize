# failure-localize

`failure-localize` is a dependency-free, provider-neutral CLI for locating the
first observable tool-call failure in a small normalized agent trace.

It answers a deliberately narrow question:

> Which event is the earliest evidence of a malformed, unavailable, or failed
> tool call, and which later events are linked to it?

The output is deterministic and fail-closed. It does not infer hidden model
intent, replay a run, choose retry counts, or handle credentials and network
traffic.

## Why this exists

Public framework discussions describe the same operational failure in different
systems: malformed or truncated tool calls are reported with too little context,
retries can repeat the same mistake, and durable workflow engines may retry a
deterministic validation error as if it were transient.

- [LangGraph #7138](https://github.com/langchain-ai/langgraph/issues/7138)
- [LangGraph #6574](https://github.com/langchain-ai/langgraph/issues/6574)
- [Pydantic AI #5178](https://github.com/pydantic/pydantic-ai/issues/5178)
- [Pydantic AI #6979](https://github.com/pydantic/pydantic-ai/issues/6979)
- [OpenAI Agents #325](https://github.com/openai/openai-agents-python/issues/325)

Those projects have framework-specific fixes and retry controls. This small
artifact tests a narrower, cross-framework boundary: whether a normalized event
record contains enough evidence to separate the first failure from its
downstream retries or workflow errors.

## Quick start

```bash
python3 failure_localize.py fixtures/truncated.json
```

The command prints stable JSON. Exit status is `0` for a localized or
insufficient trace, and `2` for malformed input.

## Input

The input is a JSON object containing an ordered `events` array. Every event has
an integer `seq`, a unique string `id`, and a string `kind`. Optional linkage
uses `call_id`, `cause_id`, or `depends_on`.

Failure signals are explicit rather than inferred from free text:

- `finish_reason: "length"` or `"max_tokens"` → `truncated_tool_call`
- `finish_reason: "MALFORMED_FUNCTION_CALL"` → `truncated_tool_call`
- `tool_found: false` → `unknown_tool`
- `arguments_valid: false` or `validation_error: true` → `invalid_arguments`
- `status: "error"` / `"failed"` or a non-empty `error` → execution failure

Unknown fields are preserved only as input; they do not affect classification.

## Validation and stopping point

The first release is intentionally small: a schema, deterministic classifier,
secret-free fixtures, and a reviewable sample. The hypothesis is falsified if
users need provider-specific adapters, semantic trace reconstruction, or live
workflow integration before this normalized boundary is useful. No SDK,
network, LLM, or credential integration is planned without an external consumer
signal.

## Development

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
python3 -m py_compile failure_localize.py
git diff --check
```

