---
atom_family: SPEC
atom_id: AN-S-3904
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 10
  updated_at: 2026-10-29 10:13:49 +0400
---
## Summary

Admit Numeric Tiers in Project Scope Units

## Claim scope

ordinary Atoms owned by Project Scope Units.

## Claim

a Project Scope Unit **must** admit an integer Tier **>=0** for every ordinary Atom it owns. The explicit Project Goal case carries Tier `-1` under CA-R-2132. Higher integer Tiers remain admissible without an upper bound and may be assigned or raised when required by the approved governing-relation ordering.

This range rule imposes no Content-Role or Type-to-Tier restriction.
