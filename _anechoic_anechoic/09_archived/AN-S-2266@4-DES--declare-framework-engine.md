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
  version: 4
  updated_at: 2026-11-10 20:47:54 +0400
---

## Summary

Declare FRAMEWORK_ENGINE

## Claim

### Prose Claim

The receiving Scope Unit is FRAMEWORK_ENGINE. The additional local Role/Form pairs are exactly:

- Method / Direct Policy;
- Requirement / Definition;
- Requirement / Goal;
- Requirement / Rule;

- Method / Solution;

The admitted HAS_ACTIVE_SUBJECT targets are exactly the declared entities or instances at these addresses:

- `PROJECT STRUCTURE//ANECHOIC`;

- `PROJECT STRUCTURE//ANECHOIC <+ Scope Unit//PROGRAMMATIC`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development <+ Architecture <+ Communication`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development <+ Architecture <+ Component Structure`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Execution Control`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Quality <+ Verification <+ Test Design`;
- `MODEL//ANECHOIC <+ Atom/Content Role: Method`;
- `MODEL//ANECHOIC <+ Scope Unit`;

- `MODEL//ANECHOIC <+ Atom`;
- `MODEL//ANECHOIC <+ Execution/Workflow Run`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development <+ Architecture <+ Communication <+ Interface Contracts`;
- `PROJECT STRUCTURE//ANECHOIC <+ Scope Unit//AGENTIC`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development <+ Frontend Engineering`;

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
