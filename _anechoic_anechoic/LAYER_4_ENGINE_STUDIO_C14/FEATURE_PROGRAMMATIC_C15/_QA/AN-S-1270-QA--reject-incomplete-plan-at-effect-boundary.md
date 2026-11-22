---
atom_family: SPEC
atom_id: AN-S-1270
container:
  component: C15
tier: 5
context:
  lens: QA
state:
  status: active
  version: 27
  updated_at: 2026-11-10 20:47:54 +0400
---

## Summary

Reject incomplete plan at effect boundary

## Claim



### Prose Claim
one PROGRAMMATIC effect boundary refuses a plan that lacks the information
needed **to** execute its declared effect.

## Details

### Applicable conditions

apply **when** a component applies filesystem, process, clock, environment,
network, persistence, **or** logging-export effects from a decision result.

### Test case

submit one effect plan with its expected outcome **or** required ordering omitted.

### Acceptance criteria

pass **only** **when** the effect boundary returns a typed incomplete-plan result **and**
applies no effect.

### Failure disposition

reject the operation **and** correct the decision boundary **before** retrying.

### Sources

- [CA-M-425 — Separate deterministic transformations from effects and lifecycle](../05_method/CA-M-425-PROGRAMMATIC-DIRECT_POLICY--separate-deterministic-transformations-from-effects-and-lifecycle.md)
