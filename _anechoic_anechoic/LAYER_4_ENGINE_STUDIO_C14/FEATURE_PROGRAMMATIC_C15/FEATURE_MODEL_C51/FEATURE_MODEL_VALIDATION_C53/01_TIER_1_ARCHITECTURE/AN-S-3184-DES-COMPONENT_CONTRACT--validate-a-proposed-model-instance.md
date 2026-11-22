---
atom_family: SPEC
atom_id: AN-S-3184
container:
  component: C53
tier: 1
context:
  template: component_contract
  lens: DES
state:
  status: active
  version: 1
  updated_at: '2026-11-21T16:09:27.431777+00:00'
---

## Summary

Validate a proposed Model instance

## Guarantee

Given a proposed instance and the applicable Model Declarations, validate the
supplied Properties and outgoing Relations against their declared types, allowed
values, cardinalities, and endpoint constraints where applicable. Apply named
instance checks and declared uniqueness rules, including inherited uniqueness
rules, against the supplied peer populations.

Return the constructed Model instance if validation succeeds. Report a
validation error if a rule fails. The caller is responsible for writing the
validated instance.

## References

AN-S-2292, AN-S-3067, and AN-T-2947.
