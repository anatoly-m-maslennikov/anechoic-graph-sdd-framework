---
atom_family: SPEC
atom_id: AN-S-1602
container:
  component: C9
tier: 2
context:
  lens: DES
state:
  status: archived
  version: 22
  updated_at: 2026-10-25 17:32:27 +0400
---
## Summary

Permit confidence-threshold defaults and overrides

# Summary

Permit confidence-threshold defaults and overrides

## Scope

the source of a Confidence Threshold value.

## Claim

a Confidence Threshold **must** take its value from applicable direct Operator input, an explicit Property on the current Plan, the nearest enclosing Hub Plan with an explicit Property, **or** the Framework Instance Settings default; the Hub chain follows `IS_DECOMPOSITION_OF`, **not** Label spelling.

## Details
