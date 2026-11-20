---
atom_family: SPEC
atom_id: AN-S-1194
structure:
  container:
    component: C9
  tier: 2
context:
  lens: DES
state:
  status: active
  version: 43
  updated_at: 2026-11-02 18:35:20 +0400
---
## Summary

Record one Lineage Impact Analysis per changed atom revision

## Claim

### Prose Claim


`semantic_revision`, `replacement`, `carrier_only`, and equivalent `refinement` changes of admitted Atoms.


**every** `semantic_revision` **or** `replacement` of an admitted Atom **must** retain **`=1`** identifiable Lineage Impact Analysis whose primary conclusion is the impact state of that exact changed parent Revision. The assessment **may** be part of an existing completed shared review package; a separate Analysis & Advisory Atom for each changed Atom is not required. A `carrier_only` **or** equivalent `refinement` change **must** require lossless-recoding **or** equivalence Verification instead.
