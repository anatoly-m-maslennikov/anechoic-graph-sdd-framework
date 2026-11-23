---
identity:
  atom_id: CA-R-3022
  ref_id: CA-R-3022@3
context:
  container:
    scope_unit: CA-SU-14
  role: Requirement
  form: Declaration
  topics:
    main_subject: PROJECT STRUCTURE//ANECHOIC
    dependencies:
    - MODEL//ANECHOIC <+ Aspect
  tier: 1
state:
  status: archived
  version: 3
  updated_at: '2026-11-11T16:56:16+04:00'
destination:
  file:
    name: CA-R-3022@3-DECLARATION--declare-engine-aspect-hierarchy.md
    path: .anechoic_anechoic/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/04_requirement/099_archived
author: Anatoly Maslennikov
---

## Summary

Declare Engine Aspect hierarchy

## Claim scope

Engineering, UX, Documentation and Product topics used by the ANECHOIC Engine.

## Claim

### Prose Claim

ANECHOIC's Project Structure contains the following project-local Aspect hierarchy. Aspects is its grouping container; the other named nodes are concrete instances of Aspect. Each indentation is direct containment, not narrowing or automatic policy inheritance. An address begins with `PROJECT STRUCTURE//ANECHOIC  <+  Aspects` and continues with ` <+ ` and the names along that branch.

Frontend Engineering covers frontend construction. Libraries and Frameworks covers library, framework and build-tool choices; Component Authoring covers Svelte components and TypeScript; Code Style covers source organization, formatting and responsibility boundaries. Visual Design, query authoring and interface contracts retain their distinct topics.

### Formal Claim

```CFEL
# instances
PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Documentation <+ Traceability;
PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Delivery <+ Change Readiness;
PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Delivery <+ Packaging;
PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Delivery <+ Reproducibility;
PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development <+ Architecture <+ Communication <+ API;
PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development <+ Architecture <+ Communication <+ Interface Contracts;
PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development <+ Architecture <+ Component Structure;
PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development <+ Authoring <+ Code Authoring <+ Python Code;
PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development <+ Authoring <+ Controlled English;
PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development <+ Authoring <+ Prompt Authoring;
PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development <+ Authoring <+ Query Authoring <+ SQL;
PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development <+ Frontend Engineering <+ Code Style;
PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development <+ Frontend Engineering <+ Component Authoring;
PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development <+ Frontend Engineering <+ Libraries and Frameworks;
PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+ Configuration;
PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+ Data Validation;
PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+ Indexing;
PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+ Output Publication;
PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+ Query Processing;
PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+ Schema;
PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+ Serialization;
PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+ Source Retrieval;
PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+ Source Selection;
PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+ State Synchronization;
PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Execution Control <+ Code Hot Reload;
PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Execution Control <+ Effect Authorization;
PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Execution Control <+ Failure Handling;
PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Execution Control <+ Outcome Reporting;
PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Execution Control <+ Recovery;
PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Execution Control <+ Resource Limits;
PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Observability <+ Logging;
PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Storage <+ Directory Layout;
PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Storage <+ Temporary State;
PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Quality <+ Performance <+ Measurement and Profiling;
PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Quality <+ Traceability <+ Provenance;
PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Quality <+ Verification <+ Coverage;
PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Quality <+ Verification <+ Dynamic Testing <+ Canary Testing;
PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Quality <+ Verification <+ Static Analysis <+ Python Code;
PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Quality <+ Verification <+ Test Data <+ Golden Corpora;
PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Quality <+ Verification <+ Test Design;
PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Product;
PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ UX <+ Discovery and Navigation;
PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ UX <+ Entry;
PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ UX <+ Guidance;
PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ UX <+ Interaction <+ Accessibility;
PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ UX <+ Interaction <+ Decision;
PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ UX <+ Result and Status Presentation;

(PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Documentation) ((INSTANCE_OF)) Aspect;
(PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Documentation <+ Traceability) ((INSTANCE_OF)) Aspect;
(PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering) ((INSTANCE_OF)) Aspect;
(PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Delivery) ((INSTANCE_OF)) Aspect;
(PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Delivery <+ Change Readiness) ((INSTANCE_OF)) Aspect;
(PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Delivery <+ Packaging) ((INSTANCE_OF)) Aspect;
(PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Delivery <+ Reproducibility) ((INSTANCE_OF)) Aspect;
(PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development) ((INSTANCE_OF)) Aspect;
(PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development <+ Architecture) ((INSTANCE_OF)) Aspect;
(PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development <+ Architecture <+ Communication) ((INSTANCE_OF)) Aspect;
(PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development <+ Architecture <+ Communication <+ API) ((INSTANCE_OF)) Aspect;
(PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development <+ Architecture <+ Communication <+ Interface Contracts) ((INSTANCE_OF)) Aspect;
(PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development <+ Architecture <+ Component Structure) ((INSTANCE_OF)) Aspect;
(PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development <+ Authoring) ((INSTANCE_OF)) Aspect;
(PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development <+ Authoring <+ Code Authoring) ((INSTANCE_OF)) Aspect;
(PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development <+ Authoring <+ Code Authoring <+ Python Code) ((INSTANCE_OF)) Aspect;
(PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development <+ Authoring <+ Controlled English) ((INSTANCE_OF)) Aspect;
(PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development <+ Authoring <+ Prompt Authoring) ((INSTANCE_OF)) Aspect;
(PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development <+ Authoring <+ Query Authoring) ((INSTANCE_OF)) Aspect;
(PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development <+ Authoring <+ Query Authoring <+ SQL) ((INSTANCE_OF)) Aspect;
(PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development <+ Frontend Engineering) ((INSTANCE_OF)) Aspect;
(PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development <+ Frontend Engineering <+ Code Style) ((INSTANCE_OF)) Aspect;
(PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development <+ Frontend Engineering <+ Component Authoring) ((INSTANCE_OF)) Aspect;
(PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development <+ Frontend Engineering <+ Libraries and Frameworks) ((INSTANCE_OF)) Aspect;
(PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation) ((INSTANCE_OF)) Aspect;
(PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Data Handling) ((INSTANCE_OF)) Aspect;
(PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+ Configuration) ((INSTANCE_OF)) Aspect;
(PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+ Data Validation) ((INSTANCE_OF)) Aspect;
(PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+ Indexing) ((INSTANCE_OF)) Aspect;
(PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+ Output Publication) ((INSTANCE_OF)) Aspect;
(PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+ Query Processing) ((INSTANCE_OF)) Aspect;
(PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+ Schema) ((INSTANCE_OF)) Aspect;
(PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+ Serialization) ((INSTANCE_OF)) Aspect;
(PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+ Source Retrieval) ((INSTANCE_OF)) Aspect;
(PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+ Source Selection) ((INSTANCE_OF)) Aspect;
(PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+ State Synchronization) ((INSTANCE_OF)) Aspect;
(PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Execution Control) ((INSTANCE_OF)) Aspect;
(PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Execution Control <+ Code Hot Reload) ((INSTANCE_OF)) Aspect;
(PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Execution Control <+ Effect Authorization) ((INSTANCE_OF)) Aspect;
(PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Execution Control <+ Failure Handling) ((INSTANCE_OF)) Aspect;
(PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Execution Control <+ Outcome Reporting) ((INSTANCE_OF)) Aspect;
(PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Execution Control <+ Recovery) ((INSTANCE_OF)) Aspect;
(PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Execution Control <+ Resource Limits) ((INSTANCE_OF)) Aspect;
(PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Observability) ((INSTANCE_OF)) Aspect;
(PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Observability <+ Logging) ((INSTANCE_OF)) Aspect;
(PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Storage) ((INSTANCE_OF)) Aspect;
(PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Storage <+ Directory Layout) ((INSTANCE_OF)) Aspect;
(PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Storage <+ Temporary State) ((INSTANCE_OF)) Aspect;
(PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Quality) ((INSTANCE_OF)) Aspect;
(PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Quality <+ Performance) ((INSTANCE_OF)) Aspect;
(PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Quality <+ Performance <+ Measurement and Profiling) ((INSTANCE_OF)) Aspect;
(PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Quality <+ Traceability) ((INSTANCE_OF)) Aspect;
(PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Quality <+ Traceability <+ Provenance) ((INSTANCE_OF)) Aspect;
(PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Quality <+ Verification) ((INSTANCE_OF)) Aspect;
(PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Quality <+ Verification <+ Coverage) ((INSTANCE_OF)) Aspect;
(PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Quality <+ Verification <+ Dynamic Testing) ((INSTANCE_OF)) Aspect;
(PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Quality <+ Verification <+ Dynamic Testing <+ Canary Testing) ((INSTANCE_OF)) Aspect;
(PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Quality <+ Verification <+ Static Analysis) ((INSTANCE_OF)) Aspect;
(PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Quality <+ Verification <+ Static Analysis <+ Python Code) ((INSTANCE_OF)) Aspect;
(PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Quality <+ Verification <+ Test Data) ((INSTANCE_OF)) Aspect;
(PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Quality <+ Verification <+ Test Data <+ Golden Corpora) ((INSTANCE_OF)) Aspect;
(PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Quality <+ Verification <+ Test Design) ((INSTANCE_OF)) Aspect;
(PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Product) ((INSTANCE_OF)) Aspect;
(PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ UX) ((INSTANCE_OF)) Aspect;
(PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ UX <+ Discovery and Navigation) ((INSTANCE_OF)) Aspect;
(PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ UX <+ Entry) ((INSTANCE_OF)) Aspect;
(PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ UX <+ Guidance) ((INSTANCE_OF)) Aspect;
(PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ UX <+ Interaction) ((INSTANCE_OF)) Aspect;
(PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ UX <+ Interaction <+ Accessibility) ((INSTANCE_OF)) Aspect;
(PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ UX <+ Interaction <+ Decision) ((INSTANCE_OF)) Aspect;
(PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ UX <+ Result and Status Presentation) ((INSTANCE_OF)) Aspect;
```
