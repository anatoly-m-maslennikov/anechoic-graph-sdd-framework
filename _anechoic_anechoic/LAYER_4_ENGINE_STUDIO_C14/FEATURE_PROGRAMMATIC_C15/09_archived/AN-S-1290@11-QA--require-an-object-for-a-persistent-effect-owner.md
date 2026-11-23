---
atom_family: SPEC
atom_id: AN-S-1290
container:
  component: C15
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 11
  updated_at: 2026-10-22 16:26:49 +0000
---
## Summary

Require an object for a persistent effect owner

# Require an object for a persistent effect owner

## Claim checked

one effect that owns identity, state, an invariant, a resource, a lifecycle, **or**
a replaceable adapter across calls is applied through a specifically named
object method.

## Test case

evaluate one standalone function that acquires a resource **and** retains its
lifecycle state for a later call.

## Acceptance criteria

pass **only** **when** the function is rejected **and** the persistent responsibility is
allocated **to** one object with explicit acquisition, use, **and** release boundaries.

## Failure disposition

reject the effect boundary **until** its persistent owner is explicit.

## Sources

- [CA-M-425 — Separate deterministic transformations from effects and lifecycle](../05_method/CA-M-425-PROGRAMMATIC-STANDARD-IMPLEMENTATION_METHOD--separate-deterministic-transformations-from-effects-and-lifecycle.md)
