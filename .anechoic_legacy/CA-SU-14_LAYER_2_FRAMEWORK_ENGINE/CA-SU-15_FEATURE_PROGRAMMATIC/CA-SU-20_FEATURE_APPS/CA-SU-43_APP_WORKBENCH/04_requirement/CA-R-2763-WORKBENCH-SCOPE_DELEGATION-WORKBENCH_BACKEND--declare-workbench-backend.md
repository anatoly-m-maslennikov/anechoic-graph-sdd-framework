---
identity:
  atom_id: CA-R-2763
  ref_id: CA-R-2763
context:
  container:
    scope_unit: CA-SU-43
  role: Requirement
  form: Scope Delegation
  topics:
    main_subject: PROJECT STRUCTURE//ANECHOIC <+ Scope Unit//WORKBENCH_BACKEND
  tier: 3
state:
  status: Active
  version: 7
  updated_at: 2026-11-11 15:29:41 +0400
destination:
  file:
    name: CA-R-2763-WORKBENCH-SCOPE_DELEGATION-WORKBENCH_BACKEND--declare-workbench-backend.md
    path: .anechoic_anechoic/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/CA-SU-15_FEATURE_PROGRAMMATIC/CA-SU-20_FEATURE_APPS/CA-SU-43_APP_WORKBENCH/04_requirement
current_scope_unit: WORKBENCH
claim_target_scope_unit: WORKBENCH_BACKEND
author: Anatoly Maslennikov
---

## Summary

Declare WORKBENCH_BACKEND

## Claim

### Prose Claim

Own Workbench source reading, indexing, relation materialization, DuckDB and DuckPGQ query execution, shared source-adapter updates under CA-R-2728, stable paged results, saved-item Journal storage and read-only schema metadata. Shared Workbench requirements and cross-interface contracts remain in WORKBENCH. Existing legacy `q_<hex>.sql` and `w_<hex>.json` files are read-only fallback sources.

The receiving Scope Unit is WORKBENCH_BACKEND. The admitted HAS_ACTIVE_SUBJECT targets are exactly the declared entities or instances at these addresses:

- `MODEL//ANECHOIC <+ CFEL <+ Relation`;
- `MODEL//ANECHOIC <+ Projection`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development <+ Architecture <+ Communication <+ Interface Contracts`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+ Indexing`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+ Query Processing`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+ Schema`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+ Source Retrieval`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+ State Synchronization`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Execution Control <+ Failure Handling`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Observability <+ Logging`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Storage <+ Temporary State`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Quality <+ Performance <+ Measurement and Profiling`;
