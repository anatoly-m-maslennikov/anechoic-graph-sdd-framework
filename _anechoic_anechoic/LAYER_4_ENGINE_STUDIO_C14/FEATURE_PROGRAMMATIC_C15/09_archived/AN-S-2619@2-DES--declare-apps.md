---
atom_family: SPEC
atom_id: AN-S-2619
container:
  component: C15
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 2
  updated_at: 2026-11-08 22:18:08 +0400
---
## Summary

Declare APPS

## Claim

### Formal Claim

```CFEL
# instances
Scope Unit//APPS.ID == "CA-SU-20";

Scope Unit//APPS.Name == "APPS";

Scope Unit//APPS.Label == "FEATURE";

Scope Unit//APPS.order.ordered == false;

Scope Unit//APPS ((IS_CONTAINED_BY)) Scope Unit//PROGRAMMATIC
```


### Prose Claim

The additional admitted local Role/Form pairs are `Requirement/Solution` and `Requirement/Scope Delegation`; existing default admissions remain unchanged. Eligible active targets are exactly the declared model entities or declared instances resolved at following existing active Subject addresses: `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Architecture/Communication`, `ANECHOIC_STRUCTURE <+ Scope Unit//GRAPH_UI`, and `ANECHOIC_STRUCTURE <+ Scope Unit//WORKBENCH`. The selection contains those exact objects, not strings, type members, or descendants; an unresolved diagnostic grants none. These permissions apply only to local Atoms whose Header.Container-derived IS_CONTAINED_BY target is Scope Unit//APPS.
