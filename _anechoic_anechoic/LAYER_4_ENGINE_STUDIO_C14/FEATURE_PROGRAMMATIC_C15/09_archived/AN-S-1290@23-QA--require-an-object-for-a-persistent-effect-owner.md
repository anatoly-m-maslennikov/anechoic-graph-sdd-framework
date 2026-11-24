---
atom_family: SPEC
atom_id: AN-S-1290
container:
  component: C15
tier: 5
context:
  lens: QA
state:
  status: archived
  version: 23
  updated_at: 2026-11-10 20:47:54 +0400
---

## Summary

Require an object for a persistent effect owner

## Claim



### Prose Claim
one effect that owns identity, state, an invariant, a resource, a lifecycle, **or**
a replaceable adapter across calls is applied through a specifically named
object method.

## Details

### Test case

evaluate one standalone function that acquires a resource **and** retains its
lifecycle state for a later call.

### Acceptance criteria

pass **only** **when** the function is rejected **and** the persistent responsibility is
allocated **to** one object with explicit acquisition, use, **and** release boundaries.

### Failure disposition

reject the effect boundary **until** its persistent owner is explicit.

### Sources

- [CA-M-425 — Separate deterministic transformations from effects and lifecycle](../05_method/CA-M-425-PROGRAMMATIC-DIRECT_POLICY--separate-deterministic-transformations-from-effects-and-lifecycle.md)
