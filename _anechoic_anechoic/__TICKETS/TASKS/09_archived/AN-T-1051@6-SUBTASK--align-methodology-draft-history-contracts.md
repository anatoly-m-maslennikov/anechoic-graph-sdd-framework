---
atom_family: TKT
atom_id: AN-T-1051
container:
  component: C00
priority: 2
context:
  template: task
  label: Subtask
state:
  status: archived
  version: 6
  updated_at: 2026-10-24 08:22:45 +0400
---
## Summary

Align methodology Draft-history contracts

# Summary

Align methodology Draft-history contracts

## Objective

Remove mandatory retained Draft-head/lineage/consuming-successor prerequisites from methodology Status/create/update contracts. Preserve ID allocation and collision checks, exact actual predecessor archives and truthful effects.

## Details

### Observed completion — 2026-10-16

CA-D-568/570/446/276/288 were aligned with exact predecessor archives and CA-A-1192–1196. Ordinary ID-free Draft promotion always allocates a fresh unused ID, including a tool-demoted Draft; actual historical IDs are not restored. Exact actual predecessor history remains preserved without a retained-head/lineage admission gate.

Estimated own work: at most 15 minutes. Use the complete current mrt_programmatic_methods prompt. Preserve unrelated work; no speculative behavior, fabricated history or unrelated status cascade. Source edits retain exact predecessors and actual N+1/time.

### Definition of Done

The bounded contracts are aligned or an exact blocker is recorded. Evidence and independent review distinguish authoritative source changes from code, tests and connected runtime acceptance. Review/update the next dependent task before execution.
