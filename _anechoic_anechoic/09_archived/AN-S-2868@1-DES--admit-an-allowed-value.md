---
atom_family: SPEC
atom_id: AN-S-2868
container:
  component: C00
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 1
  updated_at: 2026-11-05 14:25:52 +0400
---
## Summary

Admit an allowed value

## Claim

### Prose Claim

`X :: Y` admits Y as an allowed value of X in a Formal Claim. Allowed cardinality bounds use `{::n}`, `{::n+}` or `{::n..m}` and specify the allowed count of the qualified selection, not the number of distinct values in its domain. Neither form is assignment or an IS_ALLOWED_VALUE_OF Relation.
