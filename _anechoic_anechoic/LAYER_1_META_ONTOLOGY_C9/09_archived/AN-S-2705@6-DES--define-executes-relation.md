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
  version: 6
  updated_at: 2026-11-02 00:18:22 +0400
---
## Summary

Define EXECUTES Relation

## Claim

EXECUTES connects an actual Runtime to a Workflow Run it executes. The stored direction is Runtime to Workflow Run. IS_EXECUTED_BY is its declared derived inverse and is not a second stored fact.

### Formal claim

```text
CFEL > Relation//EXECUTES
CFEL > Relation//IS_EXECUTED_BY
```

## Details

This named Type uses the general `((RELATION_TYPE))` form. It has no dedicated short Subject operator. This defines the reusable Type and its derived reverse view; it creates no Runtime or actual endpoint tuple.
