---
atom_family: SPEC
atom_id: AN-S-3771
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: archived
  version: 22
  updated_at: 2026-10-23 03:14:50 +0400
---
## Summary

Size Structural Level Prefixes Dynamically

# Summary

Size Structural Level Prefixes Dynamically

## Scope

Project-internal numeric Scope Unit Directory Carrier prefixes that use the default Scope Unit directory convention.

## Claim

**when** the default Scope Unit directory convention is used, **every** Project-internal numeric Scope Unit Directory Carrier prefix **must** concatenate these components **without** a separator:

- the Structural Level, using the decimal digit count of the greatest current Project Structural Level as its width.
- the Navigational Order Number, using the decimal rendering governed by CA-D-380-CORE_META_MODEL-DELIVERY--serialize-navigational-order-numbers.

the total prefix width is the sum of those component widths, **not** a fixed limit on the Navigational Order Number. decoding consumes the Structural Level width first **and** treats the remaining digits as the Navigational Order Number. a declared native Carrier binding under CA-D-445-CORE_META_MODEL-GENERAL-DELIVERY--admit-explicit-scope-unit-carrier-bindings **must not** be reinterpreted through this default convention.

## Details
