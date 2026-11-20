---
atom_family: SPEC
atom_id: AN-S-1286
structure:
  container:
    component: C15
  tier: 5
context:
  lens: QA
state:
  status: active
  version: 23
  updated_at: 2026-11-10 20:47:54 +0400
---
## Summary

Reject an object without persistent ownership

## Claim



### Prose Claim
#### Claim checked

one PROGRAMMATIC object is admitted **only** **when** it requires identity across calls
**and** owns state, an invariant, a resource, a lifecycle, **or** a replaceable
adapter.

#### Test case

evaluate one changed object that **only** wraps a bounded one-shot effect **and** owns
no responsibility across calls.

#### Acceptance criteria

pass **only** **when** the object is rejected **and** the effect is allocated **to** a
specifically named bounded function.

#### Failure disposition

reject the object **until** persistent ownership is demonstrated **or** the wrapper is
replaced by a function.

#### Sources

- [CA-M-408 — Allocate owned state and lifecycle to objects](../05_method/CA-M-408-PROGRAMMATIC-ENG_POLICY--allocate-owned-state-and-lifecycle-to-objects.md)
