---
atom_family: SPEC
atom_id: AN-S-3981
container:
  component: C00
tier: 4
context:
  lens: QA
state:
  status: archived
  version: 14
  updated_at: 2026-09-21 00:39:50 +0000
---
## Summary

Principle-first alignment

# Principle-first alignment

## Claim checked

for **every** selected Structural Level **and** given scope, the complete active Atom set is aligned with **every** active Project Principle.

## Check

load the complete active Project Principle set first, resolve the Structural Level **and** scope, collect the complete active Atom set, including Methodology source Atoms within the selected Scope, **and** evaluate **every** Atom against **every** Principle **before** applying lower-tier authority.

## Acceptance

pass **only** **when** no Atom conflicts with a Project Principle **and** no lower-tier interpretation weakens **or** overrides one.

## Failure

report **every** conflicting Atom **and** Principle pair; route **every** conflict between active Project Principles **to** the Operator under `CA-R-1551`.
