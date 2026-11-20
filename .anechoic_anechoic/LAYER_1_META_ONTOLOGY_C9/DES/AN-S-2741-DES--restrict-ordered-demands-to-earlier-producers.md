---
identity:
  atom_id: AN-S-2741
context:
  container:
    component: C9
  tier: 5
  lens: DES
state:
  status: active
  version: 37
  updated_at: 2026-11-02 08:06:47 +0400
---
## Summary
Restrict ordered Demands to earlier Producers

## Claim

### Prose Claim


Demand Atoms whose Consumer Atom Scope Unit and Producer Claim Target Scope Unit are ordered siblings.


**if** a Demand Atom's Consumer Atom Scope Unit **and** Producer Claim Target Scope Unit are ordered siblings, **then** its Producer Claim Target Scope Unit **must** precede its Consumer Atom Scope Unit.
