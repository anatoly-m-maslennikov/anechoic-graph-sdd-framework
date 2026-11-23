---
atom_family: SPEC
atom_id: AN-S-2135
container:
  component: C9
tier: 2
context:
  lens: DES
state:
  status: archived
  version: 23
  updated_at: '2026-11-11T19:34:00+04:00'
---
## Summary

Register Core Concern Status Values

## Claim

### Prose Claim


the Core Concern Status model.


the Core Concern Status model **must** inherit the allowed values of Atom.Header.Status and add (Resolved, Canceled).

### Formal Claim

```CFEL
# model
Atom/(.Header.Context.Role in (Concern)).Header.State.Status :: Resolved;

Atom/(.Header.Context.Role in (Concern)).Header.State.Status :: Canceled;

Atom/(.Header.State.Status := Resolved).Header.State.Status >| (Status Order Number == 21);
```
