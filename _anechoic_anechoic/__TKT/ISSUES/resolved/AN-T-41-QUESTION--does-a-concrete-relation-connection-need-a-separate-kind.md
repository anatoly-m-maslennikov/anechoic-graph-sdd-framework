---
atom_family: TKT
atom_id: AN-T-41
structure:
  container:
    component: C00
  priority: 2
context:
  template: question
state:
  status: "resolved"
  version: 1
  updated_at: "2026-11-20T20:34:46.100822+00:00"
---
## Summary

Does a concrete Relation connection need a separate kind?

## Question

Should the chosen continuation below change when a concrete conflicting use is identified?

## Details

For now an actual directed connection remains the tuple (source, Relation Type, target), without a new Connection entity or separate ID. R2247 preserves source/target reference meanings; R1986 and R1987 were retired because those are not reusable Type metadata. Existing direct facts and derived inverses stay governed. A separate endpoint-record kind can be reconsidered only if a concrete operation needs it.

Latest 48-hour input and Current source meanings support this minimal continuation but do not fix every representation detail. The Operator directed choosing the best option, tracking uncertainty and continuing.
