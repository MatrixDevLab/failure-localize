# Roadmap

## V0 — bounded falsification

- [x] Document the external problem and boundary.
- [ ] Define a minimal normalized event schema.
- [ ] Implement deterministic first-failure classification.
- [ ] Add secret-free fixtures for malformed, unavailable, execution, and
  insufficient traces.
- [ ] Review the complete diff and run local checks.

## Stop / continue decision

Continue only if the fixture corpus demonstrates a useful, framework-neutral
boundary without adapters or semantic inference. Otherwise stop at the schema
and document the failed hypothesis.

## Explicitly deferred

Adapters, trace ingestion, dashboards, network integrations, LLM analysis,
retry execution, and production workflow hooks require an external consumer
signal.

