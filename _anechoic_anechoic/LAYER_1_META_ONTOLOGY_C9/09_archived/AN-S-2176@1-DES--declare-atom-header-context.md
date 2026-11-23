---
atom_family: SPEC
atom_id: AN-S-2176
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 1
  updated_at: 2026-11-11 16:27:40 +0400
---

## Summary

Declare Atom.Header.Context

## Claim

### Prose Claim

A Role-specific group uses the Role name. A Form-specific group is nested in its Role-specific group and uses the Form name.

### Formal Claim

```CFEL
# model
Atom.Header.Context{::1} :: []{::0};

Atom.Header.Context.*[in (Container, Role, Form, Label, Topics, Tier, Plan, Concern)]{::5..7};

Atom.Header.Context.Container ;> Atom.Header.Context.Role;

Atom.Header.Context.Role ;> Atom.Header.Context.Form;

Atom.Header.Context.Form ;> Atom.Header.Context.Label;

Atom.Header.Context.Label ;> Atom.Header.Context.Topics;

Atom.Header.Context.Topics ;> Atom.Header.Context.Tier
```
