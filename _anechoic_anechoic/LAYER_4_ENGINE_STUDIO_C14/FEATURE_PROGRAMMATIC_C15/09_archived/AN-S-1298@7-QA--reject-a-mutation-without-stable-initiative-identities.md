---
atom_family: SPEC
atom_id: AN-S-1298
container:
  component: C15
tier: 4
context:
  lens: QA
state:
  status: archived
  version: 7
  updated_at: 2026-09-01 02:00:00 +0400
---
## Summary

Reject a mutation without stable Initiative identities

# Reject a mutation without stable Initiative identities

## Claim checked

one programmatic mutation is blocked **before** its first effect **when** its sealed
Initiative **or** stable action identity is missing **or** replaced.

## Test case

submit one mutation whose worker replaces the stable action identity with its
queue-parent identity **before** applying the effect.

## Acceptance criteria

pass **only** **when** the mutation returns an explicit blocked outcome **and** applies no
effect.

## Failure disposition

reject dispatch **until** the original Initiative **and** action identities are
restored.

## Sources

- [CA-M-191 — Bind one programmatic mutation to its Initiative](../05_method/CA-M-191-PROGRAMMATIC-METHOD--bind-one-programmatic-mutation-to-its-initiative.md)
