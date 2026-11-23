---
atom_family: SPEC
atom_id: AN-S-2602
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 2
  updated_at: 2026-11-02 00:18:22 +0400
---

## Summary

Declare Step

## Claim

```CFEL
Atom/(.Role: Operations)/Step;
Step//{:1}((IS_CONTAINED_BY)) Workflow//;
((Step//{:1+}((CONTAINS)) Substep//)
AND (Step//{:0}((RUN)) Action//))
OR
((Step//{:0}((CONTAINS)) Substep//)
AND (Step//{:1}((RUN)) Action//))
```

## Semantics

A Step is a unit of work within a Workflow. It runs an Action or contains Substeps.
