---
atom_family: SPEC
atom_id: AN-S-2768
container:
  component: C9
tier: 1
context:
  lens: DevOps
state:
  status: archived
  version: 25
  updated_at: 2026-10-29 07:17:24 +0400
---
## Summary

Prohibit Persisting Derived Containment

# Summary

Prohibit Persisting Derived Containment

## Scope

`CONTAINS` **and** `IS_CONTAINED_BY` relations derived from canonical Carrier nesting.

## Claim

`CONTAINS` **and** `IS_CONTAINED_BY` relations derived from canonical Carrier nesting **must not** be persisted as independent relation declarations.

## Details

This prohibition applies when canonical Carrier nesting already owns the containment fact. It does not ban an independently authored direct IS_CONTAINED_BY fact whose authority is the child's admitted relation declaration rather than nesting. Do not maintain both as independent sources for the same fact. CONTAINS remains a derived inverse in either representation and is not independently authored.
