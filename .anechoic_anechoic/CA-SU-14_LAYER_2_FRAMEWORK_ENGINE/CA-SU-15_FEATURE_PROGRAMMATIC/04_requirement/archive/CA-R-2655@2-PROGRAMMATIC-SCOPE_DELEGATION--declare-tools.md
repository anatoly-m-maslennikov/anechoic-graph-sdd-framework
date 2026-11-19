---
identity:
  atom_id: CA-R-2655
  ref_id: CA-R-2655
context:
  container:
    scope_unit: CA-SU-15
  role: Requirement
  form: Scope Delegation
  topics:
    main_subject: ANECHOIC_STRUCTURE <+ Scope Unit//TOOLS
  tier: 3
state:
  status: Active
  version: 2
  updated_at: 2026-11-08 23:18:49 +0400
destination:
  file:
    name: CA-R-2655-PROGRAMMATIC-SCOPE_DELEGATION--declare-tools.md
    path: .anechoic_anechoic/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/CA-SU-15_FEATURE_PROGRAMMATIC/04_requirement
---
## Summary

Declare TOOLS

## Claim

### Formal Claim

```CFEL
# instances
Scope Unit//TOOLS.ID == "CA-SU-16";

Scope Unit//TOOLS.Name == "TOOLS";

Scope Unit//TOOLS.Label == "FEATURE";

Scope Unit//TOOLS.order.ordered == false;

Scope Unit//TOOLS ((IS_CONTAINED_BY)) Scope Unit//PROGRAMMATIC
```


### Prose Claim

The explicit default Role/Form pairs below are: `Requirement/Requirement`, `Requirement/Declaration`, `Requirement/Scope Delegation`, `Method/Decision`, `Evaluation/Decision`, `Evaluation/Eval Case`, `Delivery/Decision`, `Operations/Decision`, `Operations/Workflow`, `Operations/Step`, `Operations/Action`. Existing global default admissions, including existing Declaration families, remain unchanged; no additional pairs are granted. No exact Current Solution, Direct Policy, or Approach Policy Role/Form pair is selected. Implementation / Code Synopsis remains admitted by the global default, and Plan / Work Report remains admitted only for an already admitted Task with the same Container and within the selected target boundary.

For every admitted local Atom, the Header.Container-derived IS_CONTAINED_BY target must be exactly `Scope Unit//TOOLS` (`CA-SU-16`). Its HAS_ACTIVE_SUBJECT target is closed to exactly the declared model entities or declared instances resolved at these Current local main Subject addresses:
- `Scope Unit`
- `Subject/ANECHOIC/Carrier/File`
- `Subject/ANECHOIC/Carrier/File.Extension`
- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Architecture/Communication`
- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Architecture/Component Structure`
- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Data Handling/Data Transformation`
- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Data Handling/Data Validation`
- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Data Handling/Output Publication`
- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Data Handling/Parsing`
- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Data Handling/Serialization`
- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Data Handling/Source Retrieval`
- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Data Handling/Source Selection`
- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Delivery`
- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Delivery/Extension Lifecycle`
- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Execution Control`
- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Execution Control/Failure Handling`
- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Storage`
- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Storage/Directory Layout`
- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Verification`
- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Verification/Coverage`
- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Verification/Dynamic Testing`
- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Verification/Static Analysis`
- `Subject/ANECHOIC/Graph/Node/Project Model/Atom.Content`
- `Subject/ANECHOIC/Graph/Node/Project Model/Atom.ID`
- `Subject/ANECHOIC/Graph/Node/Project Model/Atom.Status`
- `Subject/ANECHOIC/Graph/Node/Project Model/Atom.Subjects`
- `Subject/ANECHOIC/Graph/Node/Project Model/Atom.Summary`
- `Subject/ANECHOIC/Graph/Node/Project Model/Atom.Tier`
- `Subject/ANECHOIC/Graph/Node/Project Model/Atom.Type`
- `Subject/ANECHOIC/Graph/Node/Project Model/Atom.Version Number`
- `Subject/ANECHOIC/Graph/Node/Project Model/Atom/Content Role: Evaluation`
- `Subject/ANECHOIC/Graph/Node/Project Model/Atom/Content Role: Plan`
- `Subject/ANECHOIC/Graph/Node/Project Model/Event`
- `Subject/ANECHOIC/Graph/Node/Project Model/Execution`
- `Subject/ANECHOIC/Graph/Node/Project Model/Execution.Outcome`
- `Subject/ANECHOIC/Graph/Node/Project Model/Execution/Workflow Run`
- `Subject/ANECHOIC/Graph/Node/Project Model/Execution/Workflow Run.Provenance`
- `Subject/ANECHOIC/Graph/Node/Project Model/Execution/Workflow Run.Source Admission`
- `Subject/ANECHOIC/Graph/Node/Project Model/Governing Configuration`
- `Subject/ANECHOIC/Graph/Node/Project Model/History/Journal`
- `Subject/ANECHOIC/Graph/Node/Project Model/History/Journal.Record`
- `Subject/ANECHOIC/Graph/Node/Project Model/Implementation/Code`
- `Subject/ANECHOIC/Graph/Node/Project Model/Implementation/Code/Tool`
- `Subject/ANECHOIC/Graph/Node/Project Model/Implementation/Code/Tool.Effect Result`
- `Subject/ANECHOIC/Graph/Node/Project Model/Implementation/Code/Tool.Self Description`
- `Subject/ANECHOIC/Graph/Node/Project Model/Project`
- `Subject/ANECHOIC/Graph/Node/Project Model/Project.Settings`
- `Subject/ANECHOIC/Graph/Node/Project Model/Projection`
- `Subject/ANECHOIC/Graph/Node/Project Model/Projection/Type: Catalog`
- `Subject/ANECHOIC/Graph/Node/Project Model/Scope Unit`
- `Subject/ANECHOIC/Graph/Node/Project Model/Scope Unit.Path`
- `Subject/ANECHOIC/Graph/Node/Project Model/Selection`
- `Subject/ANECHOIC/Graph/Relation`
- `Subject/ANECHOIC/Graph/Relation.Target Reference`
- `Subject/ANECHOIC/Graph/Relation/Type`
- `Subject/ANECHOIC/Graph/Relation/Type: child_of`
- `Subject/ANECHOIC/Graph/Relation/Type: structural_parent`
- `Subject/ANECHOIC/Graph/Rule`

The selection contains exact objects only, not strings, type members, or descendants; an unresolved address grants no admission.