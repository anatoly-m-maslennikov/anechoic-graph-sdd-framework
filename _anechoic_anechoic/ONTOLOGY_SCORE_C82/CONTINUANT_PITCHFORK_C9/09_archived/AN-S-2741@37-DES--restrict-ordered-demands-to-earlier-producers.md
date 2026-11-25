---
atom_family: SPEC
atom_id: AN-S-2741
container:
  component: C9
tier: 5
context:
  lens: DES
state:
  status: "archived"
  version: 37
  updated_at: "2026-11-25T22:52:54.644402+00:00"
---
## Summary
Restrict ordered Demands to earlier Producers

## Claim

### Prose Claim


Demand Atoms whose Consumer Atom Scope Unit and Producer Claim Target Scope Unit are ordered siblings.


**if** a Demand Atom's Consumer Atom Scope Unit **and** Producer Claim Target Scope Unit are ordered siblings, **then** its Producer Claim Target Scope Unit **must** precede its Consumer Atom Scope Unit.
