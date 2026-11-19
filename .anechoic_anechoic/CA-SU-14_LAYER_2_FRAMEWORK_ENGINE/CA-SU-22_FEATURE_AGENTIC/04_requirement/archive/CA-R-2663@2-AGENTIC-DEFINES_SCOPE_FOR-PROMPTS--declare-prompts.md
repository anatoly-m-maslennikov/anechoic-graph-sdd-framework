---
atom_id: CA-R-2663
ref_id: CA-R-2663@2
role: Requirement
form: Scope Delegation
topics:
  main_subject: ANECHOIC_STRUCTURE <+ Scope Unit//PROMPTS
tier: 3
status: Archived
version: 2
updated_at: 2026-11-09 17:00:18 +0400
container:
  scope_unit: CA-SU-22
destination:
  file:
    name: CA-R-2663@2-AGENTIC-DEFINES_SCOPE_FOR-PROMPTS--declare-prompts.md
    path: .anechoic_anechoic/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/CA-SU-22_FEATURE_AGENTIC/04_requirement/archive
---

## Summary

Declare PROMPTS

## Claim

### Prose Claim

The receiving Scope Unit is PROMPTS. Existing default Role and Form admissions remain applicable. The additional local Role/Form pairs are exactly:

- Method / Solution;
- Requirement / Goal;
- Requirement / Rule;

The admitted HAS_ACTIVE_SUBJECT targets are exactly the declared entities or instances at these addresses:

- `Subject/ANECHOIC/Graph/Node/Aspect/Documentation/Traceability`;
- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Development/Authoring/Prompt Authoring`;
- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Operation/Data Handling/Output Publication`;
- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Operation/Execution Control`;
- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Operation/Execution Control/Failure Handling`;
- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Operation/Storage/Directory Layout`;
- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Quality/Traceability`;
- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Quality/Verification/Coverage`;
- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Quality/Verification/Test Data/Golden Corpora`;
- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Quality/Verification/Test Design`;
- `Subject/ANECHOIC/Graph/Node/Aspect/UX/Interaction/Decision`;
- `Subject/ANECHOIC/Graph/Node/Project Model/Execution/Step Run.Agentic Step Execution Context`;

Each address selects one endpoint object, not its descendants or all members of its kind. An unresolved address is diagnostic and grants no admission. These permissions apply only to local Atoms whose Header.Container resolves to PROMPTS. Its existing identity, Name, Label, Parent and responsibility remain unchanged.

### Formal Claim

```CFEL
# instances
Scope Unit//PROMPTS.ID == "CA-SU-24";

Scope Unit//PROMPTS.Name == "PROMPTS";

Scope Unit//PROMPTS.Label == "FEATURE";

Scope Unit//PROMPTS.order.ordered == false;

Scope Unit//PROMPTS ((IS_CONTAINED_BY)) Scope Unit//AGENTIC
```
