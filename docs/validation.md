# Validation method

The first release is validated with deterministic, secret-free fixtures.

## Required cases

1. truncated tool call with linked retries;
2. unknown tool;
3. invalid arguments;
4. execution failure after a valid call;
5. no explicit failure (`insufficient`);
6. malformed top-level or event input (non-zero exit, no partial result).

For every valid fixture, run the CLI twice and compare the bytes of the JSON
output. Run unit tests, Python compilation, and `git diff --check`.

## Evidence boundary

The result reports only explicit fields and explicit links. It must not turn an
error string, event order alone, or a retry count into a causal claim.

