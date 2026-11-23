---
atom_family: SPEC
atom_id: AN-S-1289
container:
  component: C15
tier: 5
context:
  lens: QA
state:
  status: archived
  version: 18
  updated_at: 2026-10-25 17:32:27 +0400
---
## Summary

Admit a bounded one-shot effect function

# Admit a bounded one-shot effect function

## Claim checked

one bounded one-shot effect **may** be a function **when** **every** dependency **and**
boundary is explicit **and** no identity **or** ownership persists across calls.

## Test case

evaluate one specifically named function that applies one file effect from an
explicit target **and** dependency **and** returns a typed outcome **without** retained
state.

## Acceptance criteria

pass **only** **when** the function's target, dependency, input, outcome, **and** failure
boundary are explicit **and** it owns no state, invariant, resource, lifecycle, **or**
adapter across calls.

## Failure disposition

reject the function **or** allocate an object **when** **any** persistent ownership is
required.

## Sources

- [CA-M-425 — Separate deterministic transformations from effects and lifecycle](../05_method/CA-M-425-PROGRAMMATIC-ENG_POLICY--separate-deterministic-transformations-from-effects-and-lifecycle.md)
