---
atom_family: SPEC
atom_id: AN-S-1295
container:
  component: C15
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 13
  updated_at: 2026-10-23 23:58:37 +0400
---
## Summary

Reject a hidden effect in changed source

# Reject a hidden effect in changed source

## Claim checked

one changed effect function declares its complete effect boundary **or** allocates
persistent ownership **to** an object.

## Test case

evaluate one changed function that reads the process environment implicitly
**before** writing its declared target.

## Acceptance criteria

pass **only** **when** the function is rejected **until** the environment observation is
an explicit input **or** an owned adapter boundary.

## Failure disposition

block the changed unit **until** the hidden observation is removed.

## Sources

- [CA-M-425 — Separate deterministic transformations from effects and lifecycle](../05_method/CA-M-425-PROGRAMMATIC-STANDARD-ENG_POLICY--separate-deterministic-transformations-from-effects-and-lifecycle.md)
