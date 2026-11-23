---
atom_family: SPEC
atom_id: AN-S-2741
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 26
  updated_at: 2026-10-24 01:37:42 +0400
---
## Summary

Restrict ordered Demands to earlier Producers

# Summary
Restrict ordered Demands to earlier Producers

## Scope

Demand Atoms whose Consumer Atom Scope Unit and Producer Claim Target Scope Unit are ordered siblings.

## Claim

**if** a Demand Atom's Consumer Atom Scope Unit **and** Producer Claim Target Scope Unit are ordered siblings, **then** its Producer Claim Target Scope Unit **must** precede its Consumer Atom Scope Unit.

## Details
