---
atom_family: SPEC
atom_id: AN-S-1285
container:
  component: C15
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 13
  updated_at: 2026-10-24 00:38:25 +0400
---
## Summary

Reject a class used only as a function namespace

# Reject a class used only as a function namespace

## Claim checked

one deterministic responsibility that needs no identity **or** owned state is
implemented as specifically named functions **in** a module rather than as a class
used **only** for grouping.

## Test case

evaluate one changed class whose methods are **all** static deterministic
transformations **and** whose instances own no state, invariant, resource,
lifecycle, **or** adapter.

## Acceptance criteria

pass **only** **when** the class is rejected **and** the transformations are allocated **to**
specifically named functions **in** one cohesive module.

## Failure disposition

reject the changed allocation **until** the namespace-only class is removed.

## Sources

- [CA-M-407 — Allocate deterministic transformations to functions](../05_method/CA-M-407-PROGRAMMATIC-STANDARD-ENG_POLICY--allocate-deterministic-transformations-to-functions.md)
