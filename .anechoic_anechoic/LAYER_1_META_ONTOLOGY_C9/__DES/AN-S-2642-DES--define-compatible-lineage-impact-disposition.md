---
atom_family: SPEC
atom_id: AN-S-2642
structure:
  container:
    component: C9
  tier: 2
context:
  lens: DES
state:
  status: active
  version: 28
  updated_at: 2026-11-02 00:18:22 +0400
---
## Summary

Define compatible Lineage Impact disposition

## Claim

### Prose Claim


`compatible` Lineage Impact dispositions.



When a Lineage Impact analysis addresses an Atom, `compatible` must mean the child remains valid against the parent Revision required by the gate and traversal stops without a child update; a pinned earlier Revision does not establish compatibility where the new Revision is required.

