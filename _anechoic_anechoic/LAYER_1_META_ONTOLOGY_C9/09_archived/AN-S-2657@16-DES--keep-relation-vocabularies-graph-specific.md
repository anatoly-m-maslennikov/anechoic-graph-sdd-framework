---
atom_family: SPEC
atom_id: AN-S-2657
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 16
  updated_at: 2026-10-23 03:14:50 +0400
---
## Summary

Keep relation vocabularies graph-specific

# Summary

Keep relation vocabularies graph-specific

## Scope

Relation Kinds and their graph-qualified identities in ANECHOIC Graphs.

## Claim

**every** Relation Kind **must** belong **to** **`=1`** kind of ANECHOIC Graph **and** be admitted as native **only** **in** instances of that graph kind. instances of the same graph kind governed by the same Applicable Methodology **must** reuse the same Relation Kind authority.

the owning graph kind **and** canonical name **must** determine the Relation Kind's graph-qualified identity. matching names **or** compatible endpoints **must not** make Relation Kinds from different graph kinds interchangeable.

the owning graph kind determines a Relation Kind's authority, **not** a requirement that **all** endpoints occupy the same graph. admitted cross-graph endpoints **and** source references under CA-R-1472 retain that graph-qualified ownership. another graph **may** represent a source-traceable reference **or** view of the Relation **without** registering it as native.

## Details
