# Roadmap

## V0 — bounded falsification

- [x] Document the external problem and boundary.
- [x] Define a minimal normalized event schema.
- [x] Implement deterministic first-failure classification.
- [x] Add secret-free fixtures for malformed, unavailable, execution, and
  insufficient traces.
- [x] Add a matched raw-capture versus summary-only boundary fixture.
- [x] Review the complete diff and run local checks.

## Stop / continue decision

Continue only if the fixture corpus demonstrates a useful, framework-neutral
boundary without adapters or semantic inference. The matched capture fixture
is evidence that a summary cannot substitute for an explicit termination
signal; it does not justify reconstructing hidden state or judging downstream
claims. Otherwise stop at the schema and document the failed hypothesis.

## Explicitly deferred

Adapters, trace ingestion, dashboards, network integrations, LLM analysis,
retry execution, and production workflow hooks require an external consumer
signal.
