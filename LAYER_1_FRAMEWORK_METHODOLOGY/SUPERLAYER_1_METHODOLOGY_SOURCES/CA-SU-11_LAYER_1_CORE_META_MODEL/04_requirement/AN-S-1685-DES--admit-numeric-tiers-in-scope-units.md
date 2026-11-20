---
atom_family: SPEC
atom_id: AN-S-1685
structure:
  container:
    component: C9
  tier: 3
context:
  lens: DES
state:
  status: active
  version: 3
  updated_at: 2026-11-04 09:19:08 +0400
---
## Summary

Admit Numeric Tiers in Scope Units

## Claim

### Prose Claim


ordinary Atoms owned by Scope Units in the Project.


a Scope Unit in the Project **must** admit an integer Tier **>=0** for every ordinary Atom it owns, except an Atom of Form Goal whose active Subject resolves to the Project Scope Unit root. That exact predicate carries Tier `-1` under CA-R-2132 regardless of its Container or owner. Higher integer Tiers remain admissible without an upper bound and may be assigned or raised when required by the approved governing-relation ordering.

This range rule imposes no Content-Role or Type-to-Tier restriction.
