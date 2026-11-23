---
atom_family: SPEC
atom_id: AN-S-1590
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 15
  updated_at: 2026-10-24 00:38:25 +0400
---
## Summary

Resolve Status Domains from Complete Qualified Paths

# Summary

Resolve Status Domains from Complete Qualified Paths

## Scope

Status domains resolved from complete qualified paths.

## Claim

a global Status value domain **must not** override the Status domain resolved from the complete qualified path of an Artifact Type **or** Atom Content Role **and** Type.

## Details

for Atoms, resolution from the complete qualified Content Role and Type path includes the allowed values inherited from Atom.Status and the additional values admitted for that path. Inheritance does **not** replace the qualified model with a flat global domain or remove its additions. A narrower Atom kind **must not** remove inherited Status values.

