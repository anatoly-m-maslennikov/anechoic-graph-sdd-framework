---
atom_family: SPEC
atom_id: AN-S-4249
container:
  component: C20
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 2
  updated_at: 2026-11-08 23:18:49 +0400
---
## Summary

Declare WORKFLOW_ORCHESTRATOR

## Claim

Within this delegation, the admitted local Role/Form pairs used by the reviewed current local RMEDO are exactly: Evaluation/Eval Case, already globally admitted by CA-R-3008. No additional Role/Form pair is admitted.

The admitted HAS_ACTIVE_SUBJECT targets are exactly the declared model entities or declared instances resolved at these existing active Subject addresses:

- Subject/ANECHOIC/Carrier
- Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Architecture/Communication
- Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Data Handling/Data Validation
- Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Delivery
- Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Execution Control
- Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Execution Control/Recovery
- Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Verification/Dynamic Testing
- Subject/ANECHOIC/Graph/Node/Project Model/Execution/Workflow Run
- Subject/ANECHOIC/Graph/Node/Project Model/Execution/Workflow Run.Coverage
- Subject/ANECHOIC/Graph/Node/Project Model/Scope Unit

Each entry selects that single endpoint object. It does not select the address string, other members of its type, or descendants. An unresolved entry remains a diagnostic and grants no admission.

These permissions apply only to Atoms whose Header.Container-derived IS_CONTAINED_BY target is WORKFLOW_ORCHESTRATOR.

### Formal Claim

```CFEL
# instances
Scope Unit//WORKFLOW_ORCHESTRATOR.ID == "CA-SU-2";

Scope Unit//WORKFLOW_ORCHESTRATOR.Name == "WORKFLOW_ORCHESTRATOR";

Scope Unit//WORKFLOW_ORCHESTRATOR.Label == "APP";

Scope Unit//WORKFLOW_ORCHESTRATOR.order.ordered == false;

Scope Unit//WORKFLOW_ORCHESTRATOR ((IS_CONTAINED_BY)) Scope Unit//APPS
```

