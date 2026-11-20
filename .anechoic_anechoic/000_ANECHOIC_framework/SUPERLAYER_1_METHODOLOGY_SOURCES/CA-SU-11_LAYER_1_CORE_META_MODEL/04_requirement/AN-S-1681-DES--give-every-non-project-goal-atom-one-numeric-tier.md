---
identity:
  atom_id: AN-S-1681
context:
  container:
    component: C9
  tier: 1
  lens: DES
state:
  status: active
  version: 11
  updated_at: 2026-11-04 09:19:08 +0400
---
## Summary
Give Every Non-Project-Goal Atom One Numeric Tier

## Claim

### Prose Claim

Atom other than an Atom of Form Goal whose active Subject resolves to the Project Scope Unit root.


**every** Atom other than an Atom of Form Goal whose active Subject resolves to the Project Scope Unit root **must** carry exactly one integer Tier. An ordinary Atom owned by a Scope Unit uses an integer Tier **>=0**, except for that exact Project-root Goal predicate. An Atom of Form Goal whose active Subject resolves to the Project Scope Unit root carries exactly Tier `-1` under CA-R-2132, regardless of its Container or owner.

This rule defines owner-relative ranges, not a finite set of values. Higher integers remain admissible and may be assigned or raised when required by the approved governing-relation ordering. No Content-Role or Type-to-Tier restriction is imposed.
