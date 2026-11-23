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
  version: 25
  updated_at: '2026-11-11T19:34:00+04:00'
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

Atom/(.Header.Context.Role := Plan)/(.Header.State.Status := Backlog).Header.State.Status >| Status Group == Backlog;

Atom/(.Header.Context.Role in (Plan)).Header.State.Status :: Done;

Atom/(.Header.Context.Role in (Plan)).Header.State.Status :: Canceled;

Atom/(.Header.State.Status := Backlog).Header.State.Status >| (Status Order Number == 1);

Atom/(.Header.State.Status := Done).Header.State.Status >| (Status Order Number == 20);

Atom/(.Header.State.Status := Canceled).Header.State.Status >| (Status Order Number == 40);
```
