---
atom_id: CA-R-1790
ref_id: CA-R-1790
container:
  scope_unit: CA-SU-11
role: Requirement
form: Rule
topics:
  main_subject: ANECHOIC_MODEL <+ Entity/Object/Occurrent/Execution/Step Run
  dependencies:
  - ANECHOIC_MODEL <+ Entity/Object/Occurrent/Execution/Step Run
  - ANECHOIC_MODEL <+ Entity/Object/Occurrent/Execution/Workflow Run
  - 'ANECHOIC_MODEL <+ Atom/(.Header.Context.Role := Operations)/(.Header.Context.Form := Workflow) >{1+} Atom/(.Header.Context.Role := Operations)/(.Header.Context.Form := Step)'
  - 'ANECHOIC_MODEL <+ Atom/(.Header.Context.Role := Operations)/(.Header.Context.Form := Action)'
  - 'ANECHOIC_MODEL <+ Atom/(.Header.Context.Role := Operations)/(.Header.Context.Form := Action).Execution Kind'
  - ANECHOIC_MODEL <+ Entity/Object/Occurrent/Execution/Step Run.Agentic Step Execution Context
  - ANECHOIC_MODEL <+ Atom
  - ANECHOIC_MODEL <+ Entity/Object/Continuant/Actor/Operator
  - ANECHOIC_MODEL <+ Journal
tier: 2
status: Active
version: 19
updated_at: 2026-11-02 00:18:22 +0400
carrier_destination:
  file:
    name: CA-R-1790-CORE_META_MODEL-RULE--retain-agentic-step-executor-state-and-routing.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
---
## Summary

Retain Agentic Step executor state **and** routing

## Claim

### Prose Claim


execution coordination during dispatch **or** resumption of an Agentic Step, involving the executor together with the participating session **or** separate Agent context.


the executor **must** retain execution state **and** select subsequent Steps from the Workflow's declared transitions. the participating session **or** separate Agent context performs the requested Action; it need **not** reconstruct **or** remember what the Workflow will do next.
