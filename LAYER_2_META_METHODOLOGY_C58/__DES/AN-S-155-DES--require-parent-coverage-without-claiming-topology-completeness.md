---
atom_family: SPEC
atom_id: AN-S-155
container:
  component: C00
tier: 3
context:
  lens: DES
state:
  status: active
  version: 30
  updated_at: '2026-11-22T11:00:54.983176+00:00'
relations:
  CONTRIBUTES_TO:
  - AN-S-1501
---
## Summary
Require parent coverage without claiming topology completeness

## Claim

### Prose Claim


**in** strict authority mode, **every** active tier-classified PRMEDO Atom **must** have **`>=1`** permitted active parent **unless** the applicable Type authority registers its Type as orphan-permitted.

a permitted parent is:

- the active Project Goal Atom for a Project-owned Tier 0 Atom;
- an applicable lower-global-tier Atom **in** the same structural scope, or a Tier 0 Requirement for a same-Scope Tier 0 Method, Evaluation, Delivery, or Operations Atom when the applicable typed relation admits it; **or**
- an Atom permitted by the global tier topology **in** an ancestor structural scope.

this parent-coverage condition is necessary but insufficient for authority-topology completeness **and** cannot establish Project Scope Contract completeness.
