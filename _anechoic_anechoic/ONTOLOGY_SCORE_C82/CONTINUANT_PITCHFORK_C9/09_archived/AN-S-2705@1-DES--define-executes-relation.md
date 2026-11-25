---
atom_family: SPEC
atom_id: AN-S-2705
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 1
  updated_at: 2026-10-29 07:51:41 +0400
---
## Summary

Define EXECUTES Relation

## Claim

EXECUTES connects an actual Runtime to a Workflow Run it executes. The stored direction is Runtime to Workflow Run. IS_EXECUTED_BY is its declared derived inverse and is not a second stored fact.

### Formal claim

```yaml
relation_type: EXECUTES
meaning: Connect an actual Runtime to the Workflow Run it executes.
derived_inverse: IS_EXECUTED_BY
stored_fact: direct_only
```

## Details

This named Type uses the general `((RELATION_TYPE))` form. It has no dedicated short Subject operator. This Draft defines neither an existing Runtime nor a Workflow Run relation fact.
