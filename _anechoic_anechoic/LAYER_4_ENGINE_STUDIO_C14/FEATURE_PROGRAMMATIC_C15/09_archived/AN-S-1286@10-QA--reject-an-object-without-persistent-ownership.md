---
atom_family: SPEC
atom_id: AN-S-1286
container:
  component: C15
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 10
  updated_at: 2026-10-22 12:45:09 +0400
---
## Summary

Reject an object without persistent ownership

# Reject an object without persistent ownership

## Claim checked

one PROGRAMMATIC object is admitted **only** **when** it requires identity across calls
**and** owns state, an invariant, a resource, a lifecycle, **or** a replaceable
adapter.

## Test case

evaluate one changed object that **only** wraps a bounded one-shot effect **and** owns
no responsibility across calls.

## Acceptance criteria

pass **only** **when** the object is rejected **and** the effect is allocated **to** a
specifically named bounded function.

## Failure disposition

reject the object **until** persistent ownership is demonstrated **or** the wrapper is
replaced by a function.

## Sources

- [CA-M-408 — Allocate owned state and lifecycle to objects](../05_method/CA-M-408-PROGRAMMATIC-STANDARD-IMPLEMENTATION_METHOD--allocate-owned-state-and-lifecycle-to-objects.md)
