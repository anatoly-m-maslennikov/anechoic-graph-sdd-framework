---
atom_family: SPEC
atom_id: AN-S-1607
container:
  component: C9
tier: 4
context:
  lens: DES
state:
  status: archived
  version: 16
  updated_at: 2026-10-24 11:58:20 +0400
---
## Summary

Permit implementation retry-limit defaults and overrides

# Summary

Permit implementation retry-limit defaults and overrides

## Scope

effective Implementation Retry Limit selection for a Plan or Framework Instance Settings.

## Claim

an Implementation Retry Limit **must** take its effective value from applicable direct Operator input, an explicit Property on the current Plan, the nearest enclosing Hub Plan with an explicit Property, **or** Framework Instance Settings.

- a Plan **may** have **<=1** explicit Implementation Retry Limit override, regardless of Label.
- an omitted override **must** preserve inheritance **without** copying the inherited value into that Plan.
- a retry decision **must** have **=1** valid effective limit; missing **or** ambiguous authority requires Operator disposition **before** another retry.

## Details
