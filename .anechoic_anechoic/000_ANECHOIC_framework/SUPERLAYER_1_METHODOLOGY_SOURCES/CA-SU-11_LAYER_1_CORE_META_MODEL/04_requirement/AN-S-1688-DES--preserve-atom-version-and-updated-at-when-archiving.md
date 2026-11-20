---
identity:
  atom_id: AN-S-1688
context:
  container:
    component: C9
  tier: 3
  lens: DES
state:
  status: active
  version: 2
  updated_at: 2026-11-02 00:18:22 +0400
---
## Summary

Preserve Atom Version and Updated At When Archiving

## Claim

### Prose Claim


When a Workflow archives an Atom:

1. Keep Atom.Header.Version unchanged.
2. Keep Atom.Header.Updated At unchanged.
3. Do not create a new Atom Version solely for archiving.
