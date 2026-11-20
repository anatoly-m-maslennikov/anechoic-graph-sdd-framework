---
atom_family: SPEC
atom_id: AN-S-366
structure:
  container:
    component: C9
  tier: 1
context:
  lens: DES
state:
  status: active
  version: 32
  updated_at: 2026-11-02 19:44:26 +0400
---
## Summary

Prohibit skipped Scope Unit ownership

## Claim

### Prose Claim


Scope Unit ownership through a stored structural-parent relation.


a Scope Unit **must not** own a descendant Scope Unit through a stored structural-parent relation **when** another active Scope Unit lies between them.
