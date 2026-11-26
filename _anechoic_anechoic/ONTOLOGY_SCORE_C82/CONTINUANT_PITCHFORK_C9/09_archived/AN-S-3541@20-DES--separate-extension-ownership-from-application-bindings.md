---
atom_family: SPEC
atom_id: AN-S-3541
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 20
  updated_at: 2026-10-19 15:02:16 +0400
---
## Summary

Separate Extension ownership from application bindings

# Summary

Separate Extension ownership from application bindings

## Scope

Extensions **and** their application bindings within the current project.

## Claim

an Extension is an owned capability package whose Governance Origin is internal **or** external relative **to** the current project. an Extension application is a separate binding Atom whose typed relations identify the applied Extension **and** target Scope Units.

## Details

the application binding does **not** own **or** duplicate current Extension activation **or** selected Extension revision decisions; those decisions remain owned by the Framework Instance Settings Artifact under CA-R-1207 **and** CA-R-1724.
