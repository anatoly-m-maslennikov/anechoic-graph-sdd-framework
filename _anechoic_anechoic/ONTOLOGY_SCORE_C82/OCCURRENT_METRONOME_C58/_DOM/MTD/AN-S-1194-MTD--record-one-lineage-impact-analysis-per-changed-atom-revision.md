---
atom_family: SPEC
atom_id: AN-S-1194
container:
  component: C58
tier: 2
context:
  lens: DOM/MTD
state:
  status: "active"
  version: 46
  updated_at: "2026-11-25T23:20:50.716837+00:00"
---
## Summary

Record one Lineage Impact Analysis per changed atom revision

## Claim

### Prose Claim


`semantic_revision`, `replacement`, `carrier_only`, and equivalent `refinement` changes of admitted Atoms.


**every** `semantic_revision` **or** `replacement` of an admitted Atom **must** retain **`=1`** identifiable Lineage Impact Analysis whose primary conclusion is the impact state of that exact changed parent Revision. The assessment **may** be part of an existing completed shared review package; a separate Analysis & Advisory Atom for each changed Atom is not required. A `carrier_only` **or** equivalent `refinement` change **must** require lossless-recoding **or** equivalence Verification instead.

Record the examined parent and child revisions, evidence, selected disposition, and any resulting revision, successor, or blocker. One report can cover multiple child rows under one impact conclusion. Derive the affected descendant list from declared Relations. The report preserves examined sources and Relations. Where a downstream gate depends on the revised Atom, resolve each affected branch or record what blocks it. Record explicit dispositions for non-compatible and uncertain results.
