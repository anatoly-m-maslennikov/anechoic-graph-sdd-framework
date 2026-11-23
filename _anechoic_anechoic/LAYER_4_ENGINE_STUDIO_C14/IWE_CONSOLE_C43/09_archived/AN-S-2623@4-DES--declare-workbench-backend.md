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
  version: 4
  updated_at: 2026-11-08 22:18:08 +0400
---

## Summary

Declare WORKBENCH_BACKEND

## Claim

### Prose Claim

Own Workbench source reading, indexing, relation materialization, DuckDB and DuckPGQ query execution, stable paged results, saved-item Journal storage and read-only schema metadata. Shared Workbench requirements and cross-interface contracts remain in WORKBENCH. Existing legacy `q_<hex>.sql` and `w_<hex>.json` files are read-only fallback sources.
The receiving Scope Unit is WORKBENCH_BACKEND. These permissions apply only to local Atoms whose Header.Container-derived `IS_CONTAINED_BY` target is WORKBENCH_BACKEND. Its default local admissions remain applicable. Its explicit local Role/Form pairs are Requirement / Rule, Method / Decision, Method / Solution, Evaluation / Eval Case, Delivery / Decision, and Delivery / Solution. Each selection is limited to declared model entities or declared instances resolved at [`ANECHOIC_MODEL <+ Projection`, `ANECHOIC_MODEL <+ CFEL <+ Relation`]. These selections identify endpoint objects, not strings, all members of a type, or descendants. An unresolved address is diagnostic and grants no admission.

### Formal Claim

```CFEL
# instances
Scope Unit//WORKBENCH_BACKEND.ID == "CA-SU-45";

Scope Unit//WORKBENCH_BACKEND.Name == "WORKBENCH_BACKEND";

Scope Unit//WORKBENCH_BACKEND.Label == "FEATURE";

Scope Unit//WORKBENCH_BACKEND.order.ordered == false;

Scope Unit//WORKBENCH_BACKEND ((IS_CONTAINED_BY)) Scope Unit//WORKBENCH
```

