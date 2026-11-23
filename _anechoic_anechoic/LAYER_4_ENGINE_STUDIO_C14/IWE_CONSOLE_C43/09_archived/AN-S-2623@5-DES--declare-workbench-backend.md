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
  version: 5
  updated_at: 2026-11-09 07:45:15 +0400
---

## Summary

Declare WORKBENCH_BACKEND

## Claim

### Prose Claim

Own Workbench source reading, indexing, relation materialization, DuckDB and DuckPGQ query execution, stable paged results, saved-item Journal storage and read-only schema metadata. Shared Workbench requirements and cross-interface contracts remain in WORKBENCH. Existing legacy `q_<hex>.sql` and `w_<hex>.json` files are read-only fallback sources.

The receiving Scope Unit is WORKBENCH_BACKEND. Existing default Role and Form admissions remain applicable. The additional local Role/Form pairs are exactly:

- Delivery / Solution;
- Method / Solution;
- Requirement / Rule;

The admitted HAS_ACTIVE_SUBJECT targets are exactly the declared entities or instances at these addresses:

- `ANECHOIC_MODEL <+ CFEL <+ Relation`;
- `ANECHOIC_MODEL <+ Projection`;
- `ANECHOIC_STRUCTURE <+ Aspects <+ Engineering <+ Development <+ Architecture <+ Communication <+ Interface Contracts`;
- `ANECHOIC_STRUCTURE <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+ Indexing`;
- `ANECHOIC_STRUCTURE <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+ Query Processing`;
- `ANECHOIC_STRUCTURE <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+ Schema`;
- `ANECHOIC_STRUCTURE <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+ Source Retrieval`;
- `ANECHOIC_STRUCTURE <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+ State Synchronization`;
- `ANECHOIC_STRUCTURE <+ Aspects <+ Engineering <+ Operation <+ Execution Control <+ Failure Handling`;
- `ANECHOIC_STRUCTURE <+ Aspects <+ Engineering <+ Operation <+ Observability <+ Logging`;
- `ANECHOIC_STRUCTURE <+ Aspects <+ Engineering <+ Operation <+ Storage <+ Temporary State`;
- `ANECHOIC_STRUCTURE <+ Aspects <+ Engineering <+ Quality <+ Performance <+ Measurement and Profiling`;

Each address selects one endpoint object, not the address string, other members of its type or descendants. An unresolved address is diagnostic and grants no admission. These permissions apply only to local Atoms whose Header.Container resolves to WORKBENCH_BACKEND. The Scope Unit identity, Parent, responsibility and structural tree are unchanged.

### Formal Claim

```CFEL
# instances
Scope Unit//WORKBENCH_BACKEND.ID == "CA-SU-45";

Scope Unit//WORKBENCH_BACKEND.Name == "WORKBENCH_BACKEND";

Scope Unit//WORKBENCH_BACKEND.Label == "FEATURE";

Scope Unit//WORKBENCH_BACKEND.order.ordered == false;

Scope Unit//WORKBENCH_BACKEND ((IS_CONTAINED_BY)) Scope Unit//WORKBENCH
```
