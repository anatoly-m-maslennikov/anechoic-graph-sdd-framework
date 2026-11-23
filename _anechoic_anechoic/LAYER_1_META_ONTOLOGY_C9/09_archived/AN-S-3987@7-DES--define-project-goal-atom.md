---
atom_family: SPEC
atom_id: AN-S-3987
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 7
  updated_at: 2026-10-29 07:45:28 +0400
---
## Summary

Define Project Goal Atom

## Claim scope

Requirement Atoms whose desired result targets the Project.

## Claim

A Project Goal Atom **means** a Requirement Atom of Type Project Goal whose Substance states one desired result for the Project and whose current/local owner is its Operator Actor. This is the exception to ordinary Local Scope Unit ownership. A Goal targeting a non-Project Scope Unit uses Type Goal and ordinary Scope Unit ownership instead.

## Semantics

The target is the Project; the owner is the Operator. The Operator is not a Scope Unit. Storage at Project level alone does not make a Requirement a Project Goal. Tier admission is specified by CA-R-2132.

The Project Goal retains its Operator Actor owner. CA-D-637 uses its Target Project only as the derived ordering context; ordinary Goal ownership and Scope ordering are unchanged.
