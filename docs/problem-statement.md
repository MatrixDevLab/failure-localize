# Problem statement

Agent frameworks commonly turn a malformed tool call into a retry, an opaque
exception, or a workflow-level failure. When the first observable cause is not
preserved, later retries and transport/runtime errors look like independent
failures. Operators then cannot tell whether a retry could help or is merely
repeating deterministic bad input.

## Audience

Framework and agent-tool authors who already emit structured run events but need
a small regression fixture or post-run check for first-failure localization.

## Smallest useful release

Given a normalized JSON event list, produce:

1. the earliest explicit failure signal;
2. a conservative category;
3. later linked events that may be cascades; and
4. `insufficient` when the trace does not support localization.

This is evidence classification, not causal certainty. A trace can be
well-formed and still be insufficient.

## Non-goals

- provider SDK or framework adapters;
- network calls, credentials, or execution;
- semantic interpretation of arbitrary messages;
- automatic retries or retry-policy advice beyond a bounded label;
- claiming that an event caused another event without an explicit link.

## Falsifier

Stop if a useful first release requires provider-specific event extraction,
semantic reconstruction, or an existing tool already gives this exact
cross-framework boundary with lower friction. In that case, keep the schema as
a research note rather than expanding the product.

