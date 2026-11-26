---
atom_family: SPEC
atom_id: AN-S-1194
container:
  component: C9
tier: 2
context:
  lens: DES
state:
  status: archived
  version: 19
  updated_at: 2026-09-28 06:30:40 +0400
---
## Summary

Record one Lineage Impact Analysis per changed atom revision

# Record one Lineage Impact Analysis per changed atom revision

**every** `refinement`, `semantic_revision`, **or** `replacement` of an admitted Atom **must** produce **`=1`** Lineage Impact Analysis Atom whose primary conclusion is the impact state of that exact changed parent Revision, while a `carrier_only` change **must** require lossless-recoding Verification instead.
