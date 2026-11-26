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
  version: 27
  updated_at: 2026-10-29 09:46:50 +0400
---
## Summary

Define Atom Governed Subject

## Claim scope

an Atom's governed Subject relation.

## Claim

an Atom Governed Subject **means** the Atom's exactly one GOVERNS Subject Relation for a complete Current Atom; its Relation Kind is GOVERNS. A Draft may omit it while incomplete. This is the link whose target is the canonical Subject Target governed by the Atom's role/Type-specific Content; the Relation **and** its target are distinct.

## Details

### Formal claim

```text
Atom.Subjects.Governs[string]{1}
```
