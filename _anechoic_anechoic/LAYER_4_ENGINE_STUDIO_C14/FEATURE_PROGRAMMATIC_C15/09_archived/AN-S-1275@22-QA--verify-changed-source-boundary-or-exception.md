---
atom_family: SPEC
atom_id: AN-S-1275
container:
  component: C15
tier: 6
context:
  lens: QA
state:
  status: archived
  version: 22
  updated_at: 2026-10-27 06:04:45 +0400
---
## Summary

Verify changed source boundary or exception

# Verify changed source boundary or exception

## Claim checked

one changed hand-authored PROGRAMMATIC Python executable unit above 40 logical
lines has one specific bounded exception that preserves a single
responsibility.

## Applicable conditions

apply **to** a new **or** materially changed hand-authored Python file. generated
Runtime **and** Delivery outputs are **not** applicable.

## Test case

evaluate one changed executable unit exceeding 40 logical lines **without** a
documented exception.

## Acceptance criteria

pass **only** **when** the unit is rejected **until** it is split, reduced, **or** supplied
with one exception recording its measured size, reason, bounded scope, single
responsibility, **and** condition for reconsideration.

## Failure disposition

block the changed source from claiming source-boundary conformance.

## Sources

- [CA-M-419 — Ratchet hand-authored Python source boundaries](../05_method/CA-M-419-PROGRAMMATIC-ENG_POLICY--ratchet-hand-authored-python-source-boundaries.md)
