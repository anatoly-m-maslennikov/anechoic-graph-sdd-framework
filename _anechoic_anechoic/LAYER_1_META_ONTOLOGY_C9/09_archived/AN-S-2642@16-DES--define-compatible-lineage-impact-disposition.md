---
atom_family: SPEC
atom_id: AN-S-2642
container:
  component: C9
tier: 2
context:
  lens: DES
state:
  status: archived
  version: 16
  updated_at: 2026-10-23 03:06:32 +0400
---
## Summary

Define compatible Lineage Impact disposition

# Summary

Define compatible Lineage Impact disposition

## Scope

`compatible` Lineage Impact dispositions.

## Claim

`compatible` **means** the child remains valid against the parent Revision required by the gate **and** traversal stops on that branch **without** a child update. **if** the gate requires the revised parent, **then** compatibility **must** be established against that new Revision; permission **to** consume a pinned earlier Revision **must not** establish compatibility for a gate that requires the new Revision.

## Details
