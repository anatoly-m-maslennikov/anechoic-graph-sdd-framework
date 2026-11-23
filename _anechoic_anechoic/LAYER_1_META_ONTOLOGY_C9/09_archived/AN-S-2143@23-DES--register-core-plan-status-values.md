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
  version: 23
  updated_at: 2026-11-11 13:45:22 +0400
---
## Summary

Register Core Plan Status Values

## Claim

### Prose Claim


Core Plan Status values.


the Core Plan Status model **must** inherit the allowed values of Atom.Header.Status and add (Backlog, Done, Canceled). Planned **must not** be a distinct Plan Status.

### Formal Claim

```CFEL
# model
Atom/(.Header.Context.Role in (Plan)).Header.State.Status :: Backlog;

Atom/(.Header.Context.Role in (Plan)).Header.State.Status :: Done;

Atom/(.Header.Context.Role in (Plan)).Header.State.Status :: Canceled
```
