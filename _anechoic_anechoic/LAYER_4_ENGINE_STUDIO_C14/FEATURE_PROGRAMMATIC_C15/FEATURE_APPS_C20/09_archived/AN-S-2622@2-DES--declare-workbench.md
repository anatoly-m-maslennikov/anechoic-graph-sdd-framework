---
atom_family: SPEC
atom_id: AN-S-2622
container:
  component: C20
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 2
  updated_at: 2026-11-08 22:18:08 +0400
---
## Summary

Declare WORKBENCH

## Claim

The additional admitted local Role/Form pairs are exactly: Requirement/Solution, Requirement/Direct Policy, Method/Direct Policy and Delivery/Solution. Existing default admissions under CA-R-3008 continue to apply.

The admitted HAS_ACTIVE_SUBJECT targets are exactly the declared model entities or declared instances resolved at these existing active Subject addresses:

- ANECHOIC_MODEL <+ Projection
- ANECHOIC_MODEL <+ Project
- ANECHOIC_STRUCTURE <+ Scope Unit//WORKBENCH_BACKEND
- ANECHOIC_STRUCTURE <+ Scope Unit//WORKBENCH_FRONTEND
- ANECHOIC_STRUCTURE <+ Scope Unit//CODEX_EXTENSION
- Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Architecture/Component Structure

Each entry selects that single endpoint object. It does not select the address string, other members of its type, or descendants. An unresolved entry remains a diagnostic and grants no admission.

These permissions apply only to Atoms whose Header.Container-derived IS_CONTAINED_BY target is WORKBENCH.

### Formal Claim

```CFEL
# instances
Scope Unit//WORKBENCH.ID == "CA-SU-43";

Scope Unit//WORKBENCH.Name == "WORKBENCH";

Scope Unit//WORKBENCH.Label == "APP";

Scope Unit//WORKBENCH.order.ordered == false;

Scope Unit//WORKBENCH ((IS_CONTAINED_BY)) Scope Unit//APPS
```
