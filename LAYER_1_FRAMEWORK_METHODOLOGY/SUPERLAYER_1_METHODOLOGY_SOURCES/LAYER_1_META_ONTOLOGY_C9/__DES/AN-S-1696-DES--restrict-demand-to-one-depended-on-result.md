---
atom_family: SPEC
atom_id: AN-S-1696
structure:
  container:
    component: C9
  tier: 5
context:
  lens: DES
state:
  status: active
  version: 33
  updated_at: 2026-11-02 00:18:22 +0400
---
## Summary
Restrict Demand to one depended-on result

## Claim

### Prose Claim


Demand Atoms.


**every** Demand Atom **must** constrain **`=1`** Producer result on which its Consumer's accepted Goal depends.
