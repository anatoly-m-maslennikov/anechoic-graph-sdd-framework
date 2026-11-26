---
atom_family: SPEC
atom_id: AN-S-1688
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 2
  updated_at: "2026-11-25T22:24:05.585336+00:00"
---
## Summary

Preserve Atom Version and Updated At When Archiving

## Claim

### Prose Claim


When a Workflow archives an Atom:

1. Keep Atom.Header.Version unchanged.
2. Keep Atom.Header.Updated At unchanged.
3. Do not create a new Atom Version solely for archiving.
