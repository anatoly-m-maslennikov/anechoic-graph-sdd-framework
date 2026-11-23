---
atom_family: SPEC
atom_id: AN-S-2269
container:
  component: C22
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 2
  updated_at: 2026-11-10 20:47:54 +0400
---
## Summary

Declare SKILLS

## Claim

### Prose Claim

The receiving Scope Unit is SKILLS. The additional local Role/Form pairs are:

- Method / Solution;
- Delivery / Solution;
- Requirement / Rule.


The additional admitted HAS_ACTIVE_SUBJECT targets are exactly:

- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+ Source Retrieval`;


- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Delivery <+ Packaging`;

- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development <+ Authoring <+ Prompt Authoring`;

- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Execution Control`;

- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ UX <+ Interaction`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+ Source Selection`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ UX <+ Guidance`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Quality <+ Verification`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development <+ Architecture <+ Communication <+ Interface Contracts`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Quality <+ Performance <+ Measurement and Profiling`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ UX <+ Interaction <+ Decision`;
- `MODEL//ANECHOIC <+ Actor/AI Agent`;
- `MODEL//ANECHOIC <+ Carrier`;

Each address selects one endpoint object, not other members of its kind or descendants. An unresolved address is diagnostic and grants no admission. These permissions apply only to local Atoms whose Header.Container resolves to SKILLS. Identity, Parent, responsibility and the Scope Unit tree are unchanged.

### Formal Claim

```CFEL
# instances
Scope Unit//SKILLS.ID == "CA-SU-23";

Scope Unit//SKILLS.Name == "SKILLS";

Scope Unit//SKILLS.Label == "FEATURE";

Scope Unit//SKILLS.order.ordered == false;

Scope Unit//SKILLS ((IS_CONTAINED_BY)) Scope Unit//AGENTIC
```

