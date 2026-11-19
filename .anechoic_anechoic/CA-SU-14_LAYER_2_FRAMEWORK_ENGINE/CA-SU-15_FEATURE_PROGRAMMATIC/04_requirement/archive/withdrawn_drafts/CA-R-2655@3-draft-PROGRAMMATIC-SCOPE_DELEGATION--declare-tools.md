---
identity:
  atom_id: CA-R-2655
  ref_id: CA-R-2655@3-draft
context:
  container:
    scope_unit: CA-SU-15
  role: Requirement
  form: Scope Delegation
  topics:
    main_subject: PROJECT STRUCTURE//ANECHOIC <+ Scope Unit//TOOLS
  tier: 3
state:
  status: Draft
  version: 3
  updated_at: 2026-11-10 17:28:03 +0400
destination:
  file:
    name: CA-R-2655@3-draft-PROGRAMMATIC-SCOPE_DELEGATION--declare-tools.md
    path: .anechoic_anechoic/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/CA-SU-15_FEATURE_PROGRAMMATIC/04_requirement/draft
---
## Summary

Declare TOOLS

## Claim

### Formal Claim

```CFEL
# instances
PROJECT STRUCTURE//ANECHOIC <+ Scope Unit//TOOLS.ID == "CA-SU-16";

PROJECT STRUCTURE//ANECHOIC <+ Scope Unit//TOOLS.Name == "TOOLS";

PROJECT STRUCTURE//ANECHOIC <+ Scope Unit//TOOLS.Label == "FEATURE";

PROJECT STRUCTURE//ANECHOIC <+ Scope Unit//TOOLS.order.ordered == false;

PROJECT STRUCTURE//ANECHOIC <+ Scope Unit//TOOLS ((IS_CONTAINED_BY)) PROJECT STRUCTURE//ANECHOIC <+ Scope Unit//PROGRAMMATIC
```


### Prose Claim

The explicit default Role/Form pairs below are: `Requirement/Requirement`, `Requirement/Declaration`, `Requirement/Scope Delegation`, `Method/Decision`, `Evaluation/Decision`, `Evaluation/Eval Case`, `Delivery/Decision`, `Operations/Decision`, `Operations/Workflow`, `Operations/Step`, `Operations/Action`. Existing global default admissions, including existing Declaration families, remain unchanged; no additional pairs are granted. No exact Current Solution, Direct Policy, or Approach Policy Role/Form pair is selected. Analysis & Advisory / Code Synopsis remains admitted by the global default, and Plan / Work Report remains admitted only for an already admitted Task with the same Container and within the selected target boundary.

For every admitted local Atom, the Header.Container-derived IS_CONTAINED_BY target must be exactly `PROJECT STRUCTURE//ANECHOIC <+ Scope Unit//TOOLS` (`CA-SU-16`). Its HAS_ACTIVE_SUBJECT target is closed to exactly the declared model entities or declared instances resolved at these Current local main Subject addresses:
- `MODEL//ANECHOIC <+ Scope Unit`
- `MODEL//ANECHOIC <+ Carrier/File`
- `MODEL//ANECHOIC <+ Carrier/File.Extension`
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development <+ Architecture <+ Communication`
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development <+ Architecture <+ Component Structure`
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+ Data Transformation`
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+ Data Validation`
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+ Output Publication`
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+ Parsing`
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+ Serialization`
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+ Source Retrieval`
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+ Source Selection`
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Delivery`
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Delivery <+ Extension Lifecycle`
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Execution Control`
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Execution Control <+ Failure Handling`
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Storage`
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Storage <+ Directory Layout`
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Quality <+ Verification`
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Quality <+ Verification <+ Coverage`
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Quality <+ Verification <+ Dynamic Testing`
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Quality <+ Verification <+ Static Analysis`
- `MODEL//ANECHOIC <+ Atom.Content`
- `MODEL//ANECHOIC <+ Atom.ID`
- `MODEL//ANECHOIC <+ Atom.Status`
- `MODEL//ANECHOIC <+ Atom.Subjects`
- `MODEL//ANECHOIC <+ Atom.Content.Summary`
- `MODEL//ANECHOIC <+ Atom.Tier`
- `MODEL//ANECHOIC <+ Atom.Type`
- `MODEL//ANECHOIC <+ Atom.Version Number`
- `MODEL//ANECHOIC <+ Atom/Content Role: Evaluation`
- `MODEL//ANECHOIC <+ Atom/Content Role: Plan`
- `MODEL//ANECHOIC <+ Event`
- `MODEL//ANECHOIC <+ Execution`
- `MODEL//ANECHOIC <+ Execution.Outcome`
- `MODEL//ANECHOIC <+ Execution/Workflow Run`
- `MODEL//ANECHOIC <+ Execution/Workflow Run.Provenance`
- `MODEL//ANECHOIC <+ Execution/Workflow Run.Source Admission`
- `MODEL//ANECHOIC <+ Governing Configuration`
- `MODEL//ANECHOIC <+ Journal`
- `MODEL//ANECHOIC <+ Event Record`
- `MODEL//ANECHOIC <+ Package/Project Package`
- `MODEL//ANECHOIC <+ Implementation/Code/Tool`
- `MODEL//ANECHOIC <+ Implementation/Code/Tool.Effect Result`
- `MODEL//ANECHOIC <+ Implementation/Code/Tool.Self Description`
- `MODEL//ANECHOIC <+ Project`
- `MODEL//ANECHOIC <+ Project.Settings`
- `MODEL//ANECHOIC <+ Projection`
- `MODEL//ANECHOIC <+ Projection/Type: Catalog`
- `MODEL//ANECHOIC <+ Scope Unit.Path`
- `MODEL//ANECHOIC <+ Selection`
- `Subject/ANECHOIC/Graph/Relation`
- `Subject/ANECHOIC/Graph/Relation.Target Reference`
- `Subject/ANECHOIC/Graph/Relation/Type`
- `Subject/ANECHOIC/Graph/Relation/Type: child_of`
- `Subject/ANECHOIC/Graph/Relation/Type: structural_parent`
- `Subject/ANECHOIC/Graph/Rule`

The selection contains exact objects only, not strings, type members, or descendants; an unresolved address grants no admission.