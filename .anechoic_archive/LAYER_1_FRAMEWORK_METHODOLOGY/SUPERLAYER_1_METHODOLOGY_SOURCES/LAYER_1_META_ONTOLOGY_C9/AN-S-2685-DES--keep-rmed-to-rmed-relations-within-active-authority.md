---
atom_family: SPEC
atom_id: AN-S-2685
container:
  component: C9
tier: 2
context:
  lens: DES
state:
  status: active
  version: 37
  updated_at: 2026-11-02 19:44:26 +0400
---
## Summary

Keep RMED-to-RMED Relations within Active Authority

## Claim

### Prose Claim


direct relations authored by Current RMED Atoms that target RMED Atoms.


**if** a direct relation is authored by a Current Atom with Content Role **in** (Requirement, Method, Evaluation, Delivery) **and** targets an Atom with Content Role **in** (Requirement, Method, Evaluation, Delivery), **then** the target Atom **must** be Current.
