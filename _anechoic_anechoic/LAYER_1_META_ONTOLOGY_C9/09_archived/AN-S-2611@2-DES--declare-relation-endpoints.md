---
atom_family: SPEC
atom_id: AN-S-2611
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 2
  updated_at: 2026-11-02 00:18:22 +0400
---
## Summary

Declare Relation endpoints

## Claim

A Relation Definition states its allowed Host and Target in its Formal claim where existing notation expresses the selectors; otherwise use precise prose. An endpoint signature constrains admissible links; it does not assert links between every matching pair. Cardinality annotations constrain counts independently.

Use HAS_INVERSE for a derived reverse view. Its endpoint sets are the direct Relation's sets swapped. State any displayed reverse signature consistently with that derivation; do not create a separate Definition for the inverse.
