---
atom_family: SPEC
atom_id: AN-S-1313
container:
  component: C15
tier: 1
context:
  lens: QA
state:
  status: archived
  version: 19
  updated_at: 2026-10-26 00:46:35 +0400
---
## Summary

Fuzz parsers and stateful boundaries

# Fuzz parsers and stateful boundaries

## Claim checked

broad input **or** transition spaces preserve accepted invariants under generated
valid, invalid, **and** ordered cases.

## Test case

run a bounded property **or** state-machine campaign against one parser **or**
lifecycle **and** inject an invariant-breaking generated sequence.

## Acceptance criteria

pass **only** **when** the minimal failing input **or** sequence **and** seed are preserved,
the defect is accepted **or** rejected explicitly, **and** an accepted defect gains a
deterministic regression case.

## Failure disposition

reject unreplayable generated evidence **and** keep expensive campaigns outside
synchronous Hooks.

## Sources

- [Hypothesis stateful testing](https://hypothesis.readthedocs.io/en/latest/stateful.html)
- [CA-M-285 — Select software Evaluation techniques by failure mode](../05_method/CA-M-285-PROGRAMMATIC--select-software-evaluation-techniques-by-failure-mode.md)
