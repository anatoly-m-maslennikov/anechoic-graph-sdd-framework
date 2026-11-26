---
atom_family: SPEC
atom_id: AN-S-2695
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 4
  updated_at: 2026-10-29 10:21:17 +0400
---
## Summary

Define IS_EXECUTION_OF Relation

## Claim

IS_EXECUTION_OF connects an actual execution to the reusable definition being
executed. The stored direction is Workflow Run to Workflow. HAS_EXECUTION is
its declared derived inverse, not a second stored fact.

### Formal claim

```text
Entity/Graph Syntax > Relation//IS_EXECUTION_OF
Entity/Graph Syntax > Relation//HAS_EXECUTION
```

## Semantics

Workflow Run ((IS_EXECUTION_OF)) Workflow

The reusable definition is not the execution itself. Workflow Run's binding to
one Workflow belongs in the Workflow Run Entity Definition, not in every use
of this Relation Type.

## Details

This named Type uses the general `((RELATION_TYPE))` form. It defines the reusable Type and creates no occurrence or actual endpoint tuple.
