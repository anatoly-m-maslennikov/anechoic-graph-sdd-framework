---
atom_family: SPEC
atom_id: AN-S-1296
container:
  component: C15
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 14
  updated_at: 2026-10-24 00:38:25 +0400
---
## Summary

Reject an ambiguous changed source name

# Reject an ambiguous changed source name

## Claim checked

one new **or** materially changed source unit has a specific,
intention-revealing name that states one responsibility.

## Test case

evaluate one changed class named `Manager` **without** a qualifying project term **or**
owned responsibility.

## Acceptance criteria

pass **only** **when** the class is rejected **until** its name identifies the exact
responsibility it owns.

## Failure disposition

block the changed unit from claiming naming conformance.

## Sources

- [CA-M-408 — Allocate owned state and lifecycle to objects](../05_method/CA-M-408-PROGRAMMATIC-STANDARD-ENG_POLICY--allocate-owned-state-and-lifecycle-to-objects.md)
