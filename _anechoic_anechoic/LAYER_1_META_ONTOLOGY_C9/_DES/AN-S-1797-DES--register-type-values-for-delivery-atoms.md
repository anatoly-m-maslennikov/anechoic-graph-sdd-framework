---
atom_family: SPEC
atom_id: AN-S-1797
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: active
  version: 35
  updated_at: 2026-11-02 19:44:26 +0400
---
## Summary

Register Type Values for Delivery Atoms

## Claim

### Prose Claim


`Atom/(.Header.Role := Delivery).Header.Form` values.


Policy and Decision are the Delivery Type values for reusable delivery rules and bounded delivery choices. Release and Environment describe governed things or applicability; they do not require separate Delivery Types.

## Details

Policy and Decision are defined by CA-R-2267@2 and CA-R-2268@1. Delivery Atoms use these meanings independently of their Subjects. Registration does not constrain a Type value to a particular Tier.
