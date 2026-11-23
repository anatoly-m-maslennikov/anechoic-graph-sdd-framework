---
atom_family: SPEC
atom_id: AN-S-1279
container:
  component: C15
tier: 6
context:
  lens: QA
state:
  status: archived
  version: 23
  updated_at: 2026-10-25 17:32:27 +0400
---
## Summary

Verify changed-code adoption ratchet

# Verify changed-code adoption ratchet

## Claim checked

one changed **or** new PROGRAMMATIC target within an admitted automation **or** typing
capability does **not** regress below its current passing boundary.

## Applicable conditions

apply **when** a component changes source within an admitted typing, formatting,
linting, **or** behavioral-check capability. unadmitted capability selection is
**not** applicable.

## Test case

evaluate one changed target against its current admitted passing boundary.

## Acceptance criteria

pass **only** **when** the target meets the current Method-owned boundary **or** has one
accepted Method-owned bounded exception. Configuration **and** Implementation **must**
materialize that selection, Delivery **must** govern its carrier, **and** Journal Records
**must** carry evidence of the actual result **without** becoming another selection authority.

## Failure disposition

reject the ratchet claim **and** return the target **to** its change owner.

## Sources

- [CA-M-420 — Ratchet typing and automation adoption](../05_method/CA-M-420-PROGRAMMATIC-ENG_POLICY--ratchet-typing-and-automation-adoption.md)
