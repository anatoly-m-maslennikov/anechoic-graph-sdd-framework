---
atom_family: SPEC
atom_id: AN-S-2623
container:
  component: C43
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 2
  updated_at: 2026-11-04 23:19:17 +0400
---

## Summary

Declare WORKBENCH_BACKEND

## Claim

### Formal Claim

```CFEL
# instances
Scope Unit//WORKBENCH_BACKEND.ID == "CA-SU-45";

Scope Unit//WORKBENCH_BACKEND.Name == "WORKBENCH_BACKEND";

Scope Unit//WORKBENCH_BACKEND.Label == "FEATURE";

Scope Unit//WORKBENCH_BACKEND.order.ordered == false;

Scope Unit//WORKBENCH_BACKEND ((IS_CONTAINED_BY)) Scope Unit//WORKBENCH
```

### Prose Claim

Own Workbench source reading, indexing, relation materialization, DuckDB and DuckPGQ query execution, stable paged results, saved query and Worksheet files, and read-only schema metadata. Shared Workbench requirements and cross-interface contracts remain in WORKBENCH.
