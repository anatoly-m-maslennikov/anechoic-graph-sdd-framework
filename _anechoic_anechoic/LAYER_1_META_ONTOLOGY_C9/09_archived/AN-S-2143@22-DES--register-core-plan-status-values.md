---
atom_family: SPEC
atom_id: AN-S-2143
container:
  component: C9
tier: 2
context:
  lens: DES
state:
  status: archived
  version: 22
  updated_at: 2026-11-02 00:18:22 +0400
---
## Summary

Register Core Plan Status Values

## Claim

### Prose Claim


Core Plan Status values.


the Core Plan Status model **must** inherit the allowed values of Atom.Header.Status and add (Backlog, Done, Canceled). Planned **must not** be a distinct Plan Status.
