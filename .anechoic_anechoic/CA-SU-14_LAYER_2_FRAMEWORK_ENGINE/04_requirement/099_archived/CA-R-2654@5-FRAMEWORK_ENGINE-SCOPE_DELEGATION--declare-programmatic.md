---
identity:
  atom_id: CA-R-2654
  ref_id: CA-R-2654@5
context:
  role: Requirement
  form: Scope Delegation
  topics:
    main_subject: PROJECT STRUCTURE//ANECHOIC <+ Scope Unit//PROGRAMMATIC
  tier: 3
  container:
    scope_unit: CA-SU-14
state:
  status: archived
  version: 5
  updated_at: 2026-11-11 15:29:41 +0400
destination:
  file:
    name: CA-R-2654@5-FRAMEWORK_ENGINE-SCOPE_DELEGATION--declare-programmatic.md
    path: .anechoic_anechoic/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/04_requirement/099_archived
author: Anatoly Maslennikov
---

## Summary

Declare PROGRAMMATIC

## Claim

### Prose Claim

The receiving Scope Unit is PROGRAMMATIC. The admitted HAS_ACTIVE_SUBJECT targets are exactly the declared entities or instances at these addresses:

- `MODEL//ANECHOIC <+ Scope Unit`;

- `MODEL//ANECHOIC <+ Atom`;
- `MODEL//ANECHOIC <+ Projection`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering`;

- `PROJECT STRUCTURE//ANECHOIC <+ Scope Unit//CODEX_HOOK`;


- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Storage`;

- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+ Source Selection`;

- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+ Indexing`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+ Query Processing`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+ Schema`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+ State Synchronization`;
- `PROJECT STRUCTURE//ANECHOIC <+ Scope Unit//APPS`;
- `PROJECT STRUCTURE//ANECHOIC <+ Scope Unit//CONNECTOR_TOOLS`;
- `PROJECT STRUCTURE//ANECHOIC <+ Scope Unit//MCP`;
- `PROJECT STRUCTURE//ANECHOIC <+ Scope Unit//PROJECT_TOOLS`;
- `PROJECT STRUCTURE//ANECHOIC <+ Scope Unit//TOOLS`;
- `PROJECT STRUCTURE//ANECHOIC <+ Scope Unit//TOOL_WORKFLOWS`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Delivery`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Delivery <+ Change Readiness`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Delivery <+ Reproducibility`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development <+ Architecture <+ Communication`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development <+ Architecture <+ Communication <+ Interface Contracts`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development <+ Architecture <+ Component Structure`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development <+ Authoring <+ Code Authoring`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development <+ Authoring <+ Code Authoring <+ Python Code`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+ Configuration`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+ Data Validation`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+ Source Retrieval`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Execution Control`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Execution Control <+ Code Hot Reload`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Execution Control <+ Effect Authorization`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Execution Control <+ Failure Handling`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Execution Control <+ Outcome Reporting`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Execution Control <+ Resource Limits`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Observability <+ Logging`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Storage <+ Directory Layout`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Storage <+ Temporary State`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Quality <+ Performance <+ Measurement and Profiling`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Quality <+ Traceability`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Quality <+ Traceability <+ Provenance`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Quality <+ Verification <+ Coverage`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Quality <+ Verification <+ Dynamic Testing`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Quality <+ Verification <+ Dynamic Testing <+ Canary Testing`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Quality <+ Verification <+ Static Analysis`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Quality <+ Verification <+ Static Analysis <+ Python Code`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Quality <+ Verification <+ Test Design`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ UX <+ Discovery and Navigation`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ UX <+ Result and Status Presentation`;
- `MODEL//ANECHOIC <+ Project.Settings.Temporary State`;

- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+ Serialization`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Delivery <+ Packaging`;

### Formal Claim

```CFEL
# instances
Scope Unit//PROGRAMMATIC.ID == "CA-SU-15";

Scope Unit//PROGRAMMATIC.Name == "PROGRAMMATIC";

Scope Unit//PROGRAMMATIC.Label == "FEATURE";

Scope Unit//PROGRAMMATIC.order.ordered == false;

Scope Unit//PROGRAMMATIC ((IS_CONTAINED_BY)) Scope Unit//FRAMEWORK_ENGINE;

Atom/(.Header.Context.Container.scope_unit in ("CA-SU-15"))/(.Header.Context.Role in (Delivery)).Header.Context.Form :: Direct Policy;
Atom/(.Header.Context.Container.scope_unit in ("CA-SU-15"))/(.Header.Context.Role in (Evaluation)).Header.Context.Form :: Approach Policy;
Atom/(.Header.Context.Container.scope_unit in ("CA-SU-15"))/(.Header.Context.Role in (Evaluation)).Header.Context.Form :: Direct Policy;
Atom/(.Header.Context.Container.scope_unit in ("CA-SU-15"))/(.Header.Context.Role in (Evaluation)).Header.Context.Form :: Solution;
Atom/(.Header.Context.Container.scope_unit in ("CA-SU-15"))/(.Header.Context.Role in (Method)).Header.Context.Form :: Direct Policy;
Atom/(.Header.Context.Container.scope_unit in ("CA-SU-15"))/(.Header.Context.Role in (Method)).Header.Context.Form :: Solution;
Atom/(.Header.Context.Container.scope_unit in ("CA-SU-15"))/(.Header.Context.Role in (Requirement)).Header.Context.Form :: Direct Policy;
Atom/(.Header.Context.Container.scope_unit in ("CA-SU-15"))/(.Header.Context.Role in (Requirement)).Header.Context.Form :: Goal;
Atom/(.Header.Context.Container.scope_unit in ("CA-SU-15"))/(.Header.Context.Role in (Requirement)).Header.Context.Form :: Solution;
Atom/(.Header.Context.Container.scope_unit in ("CA-SU-15"))/(.Header.Context.Role in (Delivery)).Header.Context.Form :: Solution;
Atom/(.Header.Context.Container.scope_unit in ("CA-SU-15"))/(.Header.Context.Role in (Concern)).Header.Context.Form :: Question;
Atom/(.Header.Context.Container.scope_unit in ("CA-SU-15"))/(.Header.Context.Role in (Requirement)).Header.Context.Form :: Rule;
Atom/(.Header.Context.Container.scope_unit in ("CA-SU-15"))/(.Header.Context.Role in (Concern)).Header.Context.Form :: Problem;
```
