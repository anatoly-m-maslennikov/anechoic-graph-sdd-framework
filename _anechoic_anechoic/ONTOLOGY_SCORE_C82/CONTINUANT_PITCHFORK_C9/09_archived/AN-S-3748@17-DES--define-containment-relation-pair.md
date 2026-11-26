---
atom_family: SPEC
atom_id: AN-S-3748
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 17
  updated_at: 2026-10-24 00:51:05 +0400
---
## Summary

Define Containment Relation Pair

# Summary

Define Containment Relation Pair

## Scope

Direct containment and its derived inverse, including Scope Unit containment and enabled Atom containment.

## Claim

the Containment Relation Pair **means** direct relation `IS_CONTAINED_BY` from a contained entity to its containing entity **and** inverse-derived relation `CONTAINS` from the containing entity to the contained entity.

## Details

IS_CONTAINED_BY is the direct child-to-parent direction; CONTAINS is its derived inverse and is not independently authored.

Endpoint permissions are separate constraints, not part of this definition. Existing Scope Unit capability is described by CA-R-1757; CA-R-1656, CA-R-1756 and CA-R-1660 govern parent cardinality, immediate ownership and structural-parent direction. Atom containment capability and its default are governed by CA-R-1945, with the existing Plan, Workflow and Step permissions in CA-R-1990, CA-R-1991 and CA-R-1992. Their formal Graph Rule migration remains separate. Containment does not make a contained Atom part of the containing Atom's Substance or change its owning Scope Unit. This definition does not implement or require a construction graph projection.

