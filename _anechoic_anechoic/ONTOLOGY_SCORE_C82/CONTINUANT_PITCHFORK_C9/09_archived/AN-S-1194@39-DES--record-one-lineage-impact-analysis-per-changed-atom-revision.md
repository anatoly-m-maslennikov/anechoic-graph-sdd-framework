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
  version: 39
  updated_at: 2026-10-29 10:13:49 +0400
---
## Summary

Record one Lineage Impact Analysis per changed atom revision

## Claim scope

`semantic_revision`, `replacement`, `carrier_only`, and equivalent `refinement` changes of admitted Atoms.

## Claim

**every** `semantic_revision` **or** `replacement` of an admitted Atom **must** retain **`=1`** identifiable Lineage Impact Analysis whose primary conclusion is the impact state of that exact changed parent Revision. The assessment **may** be part of an existing completed shared review package; a separate Analysis Atom for each changed Atom is not required. A `carrier_only` **or** equivalent `refinement` change **must** require lossless-recoding **or** equivalence Verification instead.
