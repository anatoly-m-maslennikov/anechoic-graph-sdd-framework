---
identity:
  atom_id: AN-S-1786
context:
  container:
    component: C9
  tier: 3
  lens: DevOps
state:
  status: draft
  version: 15
  updated_at: 2026-11-05 22:19:14 +0400
---
## Summary

Serialize numbered version-qualified Draft Atom filenames

## Claim

### Prose Claim

[CA-D-378@30-draft](CA-D-378@30-draft-CORE_META_MODEL-DECISION--serialize-assigned-atom-identities.md) defines the Draft `atom_id` marker. Assemble that exact marker as the filename's Atom-ID segment before the remaining mutable filename components.

Existing legacy Draft filenames remain readable and are not normalized, renamed, or migrated automatically.
