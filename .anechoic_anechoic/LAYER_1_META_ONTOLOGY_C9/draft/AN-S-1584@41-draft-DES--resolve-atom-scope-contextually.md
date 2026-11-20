---
identity:
  atom_id: AN-S-1584
context:
  container:
    component: C9
  tier: 3
  lens: DES
state:
  status: draft
  version: 41
  updated_at: 2026-11-05 13:47:13 +0400
---
## Summary

Resolve Atom Scope Contextually

## Claim

### Prose Claim


Atom Scope.


an Atom Scope **must** include the Scope Unit resolved from its `Header.Container` chain, its **`=1`** Atom Governed Subject, **and** **any** explicit Scope constraints **in** its Claim. Follow Atom container references until a Scope Unit ID is reached; predefined `world` (`CA-SU--1`) is a valid Scope Unit.
