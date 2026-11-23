---
atom_id: CA-R-1518
ref_id: CA-R-1518
container:
  scope_unit: CA-SU-13
role: Requirement
form: Rule
topics:
  main_subject: ANECHOIC_MODEL <+ Atom/(.Header.Context.Role := Evaluation)
  dependencies:
  - ANECHOIC_STRUCTURE <+ Entity/Object/Continuant/Selection//Methodology Sources
  - ANECHOIC_MODEL <+ Scope Unit
  - ANECHOIC_MODEL <+ Atom/(.Header.Context.Role := Operations)/(.Header.Context.Form
    := Action)
  - ANECHOIC_MODEL <+ Atom/(.Header.Context.Role := Operations)/(.Header.Context.Form
    := Workflow)
  - ANECHOIC_MODEL <+ Atom/(.Header.Context.Role := Operations)/(.Header.Context.Form
    := Workflow) >{1+} Atom/(.Header.Context.Role := Operations)/(.Header.Context.Form
    := Step)
  - ANECHOIC_MODEL <+ Package
  - ANECHOIC_MODEL <+ Atom/(.Header.Context.Role := Operations)
  - ANECHOIC_STRUCTURE <+ Aspects <+ Engineering <+ Quality <+ Verification
  - ANECHOIC_MODEL <+ Relation//evaluation_for
  - ANECHOIC_MODEL <+ Atom/(.Header.Context.Role:=Operations)/Workflow
tier: 2
status: Active
version: 25
updated_at: 2026-11-02 18:35:20 +0400
carrier_destination:
  file:
    name: CA-R-1518-PROJECT_CONFIGURATION-RULE--separate-methodology-and-tool-evaluation-responsibilities.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-13_LAYER_3_PROJECT_CONFIGURATION/04_requirement
current_scope_unit: PROJECT_CONFIGURATION
claim_target_scope_unit: PROJECT_CONFIGURATION
---
## Summary

Separate methodology and Tool Evaluation responsibilities

## Claim

### Prose Claim


Evaluation responsibility for operational definitions and their Tool implementations.


**in** the ANECHOIC Project, Evaluation responsibility for operational definitions **and** their Tool implementations **must** follow this allocation:

## Details

- methodology source Scope Units own Evaluations of Action **and** Workflow definitions, including valid Action references, Step inputs, typed transitions, **and** termination **or** bounded retry conditions. these Evaluations **may** directly check O authority under CA-R-1018; checks for Steps **and** Runs reuse CA-E-486 **when** applicable.
- TOOLS **and** its Tool Scope Units own Evaluations of Tools: implementation behavior, interfaces, failures, **and** conformance **to** the Action implemented by the Tool. these Evaluations **must not** independently define the correctness rules of the referenced Action **or** Workflow.

checking whether a Tool realizes an Action correctly is distinct from checking whether that Action's definition is valid. a Tool test **may** use the methodology definition as its expected-behavior authority **without** taking ownership of definition validation.
