---
atom_family: SPEC
atom_id: AN-S-1797
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 29
  updated_at: 2026-10-25 17:32:27 +0400
---
## Summary

Register Type Values for Delivery Atoms

# Summary

Register Type Values for Delivery Atoms

## Scope

`Atom/Content Role: Delivery/Type` values.

## Claim

Eng Policy and Eng Decision **must** be registered as internal values of `Atom/Content Role: Delivery/Type`. Release Definition and Environment Definition remain registered outside PROGRAMMATIC and its descendants.

## Details

Eng Policy and Eng Decision are defined by CA-R-2121 and CA-R-2122. Within PROGRAMMATIC and its descendants, Delivery Atoms use only those two Types. Existing specific Delivery Types remain valid outside that scope where their meanings apply. Registration does not constrain a Type value to a particular Tier.
