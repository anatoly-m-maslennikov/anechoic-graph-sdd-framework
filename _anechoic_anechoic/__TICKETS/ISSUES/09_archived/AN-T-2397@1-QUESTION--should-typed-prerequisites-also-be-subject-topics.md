---
atom_family: TKT
atom_id: AN-T-2397
container:
  component: C00
priority: 2
context:
  template: question
state:
  status: archived
  version: 1
  updated_at: 2026-10-24 07:51:34 +0400
---
## Summary

Should typed prerequisites also be Subject topics?

# Summary

Should typed prerequisites also be Subject topics?

## Question

Should an exact prerequisite Plan ID stay in Subjects when the same direct
DEPENDS_ON relation and the task's prerequisite text already preserve it?

## Scope

Eight Current Plans: P940, P945, P946, P947, P948, P949, P950 and P951.

## Details

Bounded choice: remove only these eight redundant ID-valued Subject entries.
Each source explicitly waits until that same Plan is Done and already stores
its exact ID in the typed depends_on relation. Keep that relation, its direction,
target and all body text unchanged. R2004 defines Subjects as topic expressions;
repeating the prerequisite identity there adds no distinct topic meaning.

This is not a general deletion of named instances or dependencies. No missing
relation is inferred, no prerequisite is removed, and no historical Plan is
executed or newly declared complete. Other unresolved Subjects remain visible.
