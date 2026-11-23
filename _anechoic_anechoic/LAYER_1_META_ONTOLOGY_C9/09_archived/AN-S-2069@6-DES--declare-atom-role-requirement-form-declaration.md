---
atom_family: SPEC
atom_id: AN-S-2069
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 6
  updated_at: 2026-11-11 14:06:22 +0400
---
## Summary

Declare Atom/(.Role := Requirement)/(.Form := Declaration)

## Claim

### Prose Claim


A Declaration states the applicable contract for its active Subject. Its Claim may contain several prose statements, CFEL formal expressions, or both when they form one coherent declaration about one topic.

Scope Unit Declaration is a Requirement Form using this template. It is not another Atom Role.

### Formal Claim

```CFEL
# model
Atom/(.Header.Context.Role in (Requirement)).Header.Context.Form :: Declaration;
```
