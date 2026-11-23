---
atom_family: SPEC
atom_id: AN-S-2266
container:
  component: C00
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 2
  updated_at: 2026-11-09 14:41:40 +0400
---

## Summary

Declare FRAMEWORK_ENGINE

## Claim

### Prose Claim

The receiving Scope Unit is FRAMEWORK_ENGINE. Existing default Role and Form admissions remain applicable. The additional local Role/Form pairs are exactly:

- Requirement / Definition;
- Requirement / Goal;
- Requirement / Rule;

The admitted HAS_ACTIVE_SUBJECT targets are exactly the declared entities or instances at these addresses:

- `ANECHOIC_STRUCTURE <+ Scope Unit//PROGRAMMATIC`;
- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Development/Architecture/Communication`;
- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Development/Architecture/Component Structure`;
- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Operation/Execution Control`;
- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Quality/Verification/Test Design`;
- `Subject/ANECHOIC/Graph/Node/Project Model/Atom/Content Role: Method`;
- `Subject/ANECHOIC/Graph/Node/Project Model/Scope Unit`;

Each address selects one endpoint object, not the address string, other members of its type or descendants. An unresolved address is diagnostic and grants no admission. These permissions apply only to local Atoms whose Header.Container resolves to FRAMEWORK_ENGINE. Its identity, Name, Label, Parent, order and existing responsibility remain unchanged.

### Formal Claim

```CFEL
# instances
Scope Unit//FRAMEWORK_ENGINE.ID == "CA-SU-14";

Scope Unit//FRAMEWORK_ENGINE.Name == "FRAMEWORK_ENGINE";

Scope Unit//FRAMEWORK_ENGINE.Label == "LAYER";

Scope Unit//FRAMEWORK_ENGINE.order.ordered == true;

Scope Unit//FRAMEWORK_ENGINE.order.number == 2;

Scope Unit//FRAMEWORK_ENGINE ((IS_CONTAINED_BY)) Project//anechoic
```
