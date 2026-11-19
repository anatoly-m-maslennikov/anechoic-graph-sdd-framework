---
atom_id: CA-R-1800
ref_id: CA-R-1800
container:
  scope_unit: CA-SU-13
role: Requirement
form: Rule
topics:
  main_subject: ANECHOIC_MODEL <+ Package
  dependencies:
  - ANECHOIC_MODEL <+ Atom/(.Header.Context.Role := Operations)/(.Header.Context.Form
    := Action)
  - ANECHOIC_MODEL <+ Atom/(.Header.Context.Role := Operations)/(.Header.Context.Form
    := Workflow)
  - ANECHOIC_MODEL <+ Atom/(.Header.Context.Role := Operations)/(.Header.Context.Form
    := Workflow) >{1+} Atom/(.Header.Context.Role := Operations)/(.Header.Context.Form
    := Step)
  - ANECHOIC_STRUCTURE <+ Entity/Object/Continuant/Selection//Methodology Sources
  - ANECHOIC_MODEL <+ Atom/(.Header.Context.Role := Operations)
  - ANECHOIC_STRUCTURE <+ Aspects <+ Engineering <+ Development <+ Architecture <+
    Component Structure
  - ANECHOIC_STRUCTURE <+ Aspects <+ Engineering
  - ANECHOIC_MODEL <+ Atom/(.Header.Context.Role:=Operations)/Step
tier: 3
status: Active
version: 19
updated_at: 2026-11-02 18:35:20 +0400
carrier_destination:
  file:
    name: CA-R-1800-PROJECT_CONFIGURATION-RULE--bind-every-tool-to-one-methodology-action.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-13_LAYER_3_PROJECT_CONFIGURATION/04_requirement
current_scope_unit: PROJECT_CONFIGURATION
claim_target_scope_unit: PROJECT_CONFIGURATION
---
## Summary

Bind **every** Tool to one methodology Action

## Claim

### Prose Claim


Tools in the anechoic Project.


**in** the anechoic Project, **every** Tool **must** implement **`=1`** Action defined by an existing applicable methodology O Atom.

## Details

- the Tool's RMED identifies that Action as the behavior it realizes **and** specifies its implementation obligations **without** copying the canonical Action definition.
- a Workflow Step binds its Action under CA-R-2465; the corresponding Tool realizes that Action rather than redefining the Workflow graph.
- this cardinality constrains the Action implemented by the Tool. it does **not** count internal instructions, API calls, interactions, **or** retries.

the binding is **not** a requirement **to** use that Action **or** a particular Workflow **to** build the Tool.
