---
atom_family: SPEC
atom_id: AN-S-1681
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 2
  updated_at: 2026-10-24 01:02:18 +0400
---
## Summary

Give Every Non-Project-Goal Atom One Numeric Tier

# Summary
Give Every Non-Project-Goal Atom One Numeric Tier

## Scope
Atom other than a Project Goal Atom.

## Claim

**every** non-Project-Goal Atom **must** carry exactly one integer Tier. An ordinary Atom owned by the Project uses an integer Tier **>=0**; an Atom owned by a non-Project Scope Unit uses an integer Tier **>=1**. Project Goal is the separate explicit Tier `-1` case under CA-R-2132.

This rule defines owner-relative ranges, not a finite set of values. Higher integers remain admissible and may be assigned or raised when required by the approved governing-relation ordering. No Content-Role or Type-to-Tier restriction is imposed.

## Details
