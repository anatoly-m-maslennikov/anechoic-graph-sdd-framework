---
atom_family: SPEC
atom_id: AN-S-2624
container:
  component: C43
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 2
  updated_at: 2026-11-08 22:18:08 +0400
---
## Summary

Declare WORKBENCH_FRONTEND

## Claim

### Prose Claim

Own the Workbench query UI, component palette, presentation, formatting, page navigation and frontend state. Shared Workbench requirements and cross-interface contracts remain in WORKBENCH.
The receiving Scope Unit is WORKBENCH_FRONTEND. These permissions apply only to local Atoms whose Header.Container-derived `IS_CONTAINED_BY` target is WORKBENCH_FRONTEND. Its default local admissions remain applicable. Its explicit local Role/Form pairs are Requirement / Declaration, Method / Decision, Evaluation / Eval Case, and Delivery / Decision. Each selection is limited to declared model entities or declared instances resolved at [`ANECHOIC_MODEL <+ Projection`, `PROJECT_STRUCTURE <+ Aspect//Visual Design`]. These selections identify endpoint objects, not strings, all members of a type, or descendants. An unresolved address is diagnostic and grants no admission.

### Formal Claim

```CFEL
# instances
Scope Unit//WORKBENCH_FRONTEND.ID == "CA-SU-46";

Scope Unit//WORKBENCH_FRONTEND.Name == "WORKBENCH_FRONTEND";

Scope Unit//WORKBENCH_FRONTEND.Label == "FEATURE";

Scope Unit//WORKBENCH_FRONTEND.order.ordered == false;

Scope Unit//WORKBENCH_FRONTEND ((IS_CONTAINED_BY)) Scope Unit//WORKBENCH
```

