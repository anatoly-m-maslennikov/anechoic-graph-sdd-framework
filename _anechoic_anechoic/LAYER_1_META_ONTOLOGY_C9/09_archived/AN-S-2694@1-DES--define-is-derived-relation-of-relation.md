---
atom_family: SPEC
atom_id: AN-S-2694
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 1
  updated_at: 2026-10-26 05:27:27 +0400
---
## Summary

Define is derived relation of relation

# Summary

Define is derived relation of relation

## Scope

Type-level derivation between Relation Type instances.

## Claim

`IS_DERIVED_RELATION_OF` **means** a direct relation from one derived Relation
Type instance to one source Relation Type instance from which its relation
meaning is derived.

## Details

This relation does not itself define an endpoint transformation, source-storage
direction, mandatory evidence, provenance, or inference behavior. A
pair-specific definition states any such meaning. `IS_DERIVED_RELATION_OF` is
not `DERIVED_FROM`, which links a derived Artifact Revision to an exact source
Artifact Revision.

