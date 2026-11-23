---
atom_family: SPEC
atom_id: AN-S-3551
container:
  component: C9
tier: 2
context:
  lens: DES
state:
  status: archived
  version: 28
  updated_at: 2026-10-29 09:50:47 +0400
---
## Summary

Define Atom Governed Subject

## Claim scope

an Atom's governed Subject relation.

## Claim

an Atom Governed Subject **means** the Atom's exactly one GOVERNS Subject Relation for a complete Current Atom; its Relation Kind is GOVERNS. A Draft may omit it while incomplete. Its target is the canonical Subject Target governed by the Atom's role/Type-specific Content; the Relation **and** its target are distinct.

### Formal claim

```text
Atom.Subjects.Governs[string]{1}
```


## Details

