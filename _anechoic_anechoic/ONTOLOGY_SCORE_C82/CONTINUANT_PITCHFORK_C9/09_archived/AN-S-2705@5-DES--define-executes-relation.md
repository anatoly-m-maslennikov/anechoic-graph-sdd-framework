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
  version: 5
  updated_at: 2026-10-29 10:21:17 +0400
---
## Summary

Define EXECUTES Relation

## Claim

EXECUTES connects an actual Runtime to a Workflow Run it executes. The stored direction is Runtime to Workflow Run. IS_EXECUTED_BY is its declared derived inverse and is not a second stored fact.

### Formal claim

```text
Entity/Graph Syntax > Relation//EXECUTES
Entity/Graph Syntax > Relation//IS_EXECUTED_BY
```

## Details

This named Type uses the general `((RELATION_TYPE))` form. It has no dedicated short Subject operator. This defines the reusable Type and its derived reverse view; it creates no Runtime or actual endpoint tuple.
