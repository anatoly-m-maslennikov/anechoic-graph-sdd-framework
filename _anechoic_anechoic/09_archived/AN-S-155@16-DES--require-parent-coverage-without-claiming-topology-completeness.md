---
atom_family: SPEC
atom_id: AN-S-155
container:
  component: C00
tier: 4
context:
  lens: DES
state:
  status: archived
  version: 16
  updated_at: 2026-09-17 16:16:04 +0000
---
## Summary

Require parent coverage without claiming topology completeness

# Require parent coverage without claiming topology completeness

**in** strict authority mode, **every** active tier-classified PRMEDO Atom **must** have **`>=1`** permitted active parent **unless** the applicable Type authority registers its Type as orphan-permitted.

a permitted parent is:

- the active Project Goal Atom for a Project Principle;
- an applicable lower-global-tier Atom **in** the same structural scope; **or**
- an Atom permitted by the global tier topology **in** an ancestor structural scope.

this parent-coverage condition is necessary but insufficient for authority-topology completeness **and** cannot establish Principle-set completeness.
