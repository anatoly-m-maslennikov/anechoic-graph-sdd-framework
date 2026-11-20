---
atom_id: CA-R-3012
ref_id: CA-R-3012@1
role: Requirement
form: Scope Delegation
topics:
  main_subject: ANECHOIC_STRUCTURE <+ Scope Unit//FRAMEWORK_DELIVERY
tier: 3
status: archived
version: 1
updated_at: 2026-11-09 15:54:30 +0400
container:
  scope_unit: CA-SU-00
relations:
  IS_REPLACEMENT_FOR:
  - CA-R-2666
destination:
  file:
    name: CA-R-3012@1-anechoic-DEFINES_SCOPE_FOR-FRAMEWORK_DELIVERY--declare-framework-delivery.md
    path: .anechoic_anechoic/04_requirement/099_archived
---

## Summary

Declare FRAMEWORK_DELIVERY

## Claim

### Prose Claim

Project delegates whole-project local and public release to FRAMEWORK_DELIVERY. It owns their Workflow definitions, release-specific Requirements, Methods, Evaluations and Delivery contracts, including recovery and release aftermath. Shared Engine implementation and generic contracts remain separate dependencies. The Project retains its external Goal and wider accountability.

The admitted local Role/Form pairs are exactly:

- Delivery / Decision;
- Evaluation / Eval Case;
- Method / Decision;
- Operations / Action;
- Operations / Step;
- Operations / Workflow;
- Requirement / Rule;

The admitted HAS_ACTIVE_SUBJECT targets are exactly the endpoint objects at these addresses:

- `ANECHOIC_MODEL <+ Entity/Object/Continuant/History/Release.ID`;
- `ANECHOIC_STRUCTURE <+ Aspects <+ Engineering`;
- `Subject/ANECHOIC/Carrier/Pull Request`;
- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Delivery`;
- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Operation/Data Handling/Data Validation`;
- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Operation/Data Handling/Serialization`;
- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Operation/Execution Control`;
- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Operation/Storage/Directory Layout`;
- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Quality/Verification/Dynamic Testing`;
- `Subject/ANECHOIC/Graph/Node/Project Model/History/Journal.Record`;
- `Subject/ANECHOIC/Graph/Node/Project Model/Implementation`;
- `Subject/ANECHOIC/Graph/Node/Project Model/Implementation/Code/Tool`;
- `Subject/anechoic/Action//Aggregate the full Release Gate`;
- `Subject/anechoic/Action//Finalize actual public Version History link`;
- `Subject/anechoic/Action//Prepare bound public release materials`;
- `Subject/anechoic/Action//Run host-capable Candidate E2E`;
- `Subject/anechoic/Action//Validate local release inputs`;
- `Subject/anechoic/Step//Finalize the actual public history link`;
- `Subject/anechoic/Step//Public release/Step: discover matching main PR`;
- `Subject/anechoic/Step//Public release/Step: prepare materials`;
- `Subject/anechoic/Step//Public release/Step: push and upsert main PR`;
- `Subject/anechoic/Step//Release Version/Step: build candidate image`;
- `Subject/anechoic/Step//Release Version/Step: compile applicable Methodology`;
- `Subject/anechoic/Step//Release Version/Step: deliver active sources`;
- `Subject/anechoic/Step//Release Version/Step: install product and refresh Project MCP`;
- `Subject/anechoic/Step//Release Version/Step: retire exact prior image`;
- `Subject/anechoic/Step//Release Version/Step: run closed candidate Unit gate`;
- `Subject/anechoic/Step//Release Version/Step: run host-capable Candidate E2E`;
- `Subject/anechoic/Step//Release Version/Step: stage candidate package and Skill`;
- `Subject/anechoic/Step//Release Version/Step: validate local inputs`;
- `Subject/anechoic/Workflow//Local Release`;
- `Subject/anechoic/Workflow//Public Release`;

Each address selects one endpoint object, not its descendants or all members of its kind. An unresolved address is diagnostic and grants no admission. These local permissions apply only when Header.Container resolves to FRAMEWORK_DELIVERY. Applicable model defaults remain in force.

### Formal Claim

```CFEL
# instances
Scope Unit//FRAMEWORK_DELIVERY.ID == "CA-SU-27";

Scope Unit//FRAMEWORK_DELIVERY.Name == "FRAMEWORK_DELIVERY";

Scope Unit//FRAMEWORK_DELIVERY.Label == "LAYER";

Scope Unit//FRAMEWORK_DELIVERY.order.ordered == true;

Scope Unit//FRAMEWORK_DELIVERY.order.number == 5;

Scope Unit//FRAMEWORK_DELIVERY ((IS_CONTAINED_BY)) Project//anechoic
```
