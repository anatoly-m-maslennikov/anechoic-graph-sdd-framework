---
atom_family: SPEC
atom_id: AN-S-2507
structure:
  container:
    component: C00
  tier: 6
context:
  lens: SWD
state:
  status: draft
  version: 31
  updated_at: 2026-11-02 18:35:20 +0400
---
## Summary

Evaluate Set-valued Property Membership

## Claim scope

evaluation of **in** **or** **not in** for one set-valued governed property.

## Claim

**to** evaluate **in** **or** **not in** for one set-valued governed property, the Resolver **must** evaluate **in** as true exactly **when** **`>=1`** property member **`=`** one listed value **and** **must** evaluate **not in** as true exactly **when** no property member **`=`** **any** listed value.
