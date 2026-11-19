---
atom_id: CA-R-1846
ref_id: CA-R-1846
container:
  scope_unit: CA-SU-24
role: Requirement
form: Rule
topics:
  main_subject: PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation
    <+ Execution Control
  dependencies:
  - PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Execution
    Control <+ Failure Handling
  - MODEL//ANECHOIC <+ Atom/(.Header.Context.Role := Evaluation)
  - MODEL//ANECHOIC <+ Execution/Workflow Run
  - MODEL//ANECHOIC <+ Journal
tier: 3
status: Active
version: 14
updated_at: 2026-11-10 20:47:54 +0400
carrier_destination:
  file:
    name: CA-R-1846-PROMPTS-RULE--retain-truthful-implementation-prompt-outcomes.md
    path: .anechoic_anechoic/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/CA-SU-22_FEATURE_AGENTIC/CA-SU-24_FEATURE_PROMPTS/04_requirement
current_scope_unit: PROMPTS
claim_target_scope_unit: PROMPTS
author: Anatoly Maslennikov
---
## Summary

Retain truthful implementation prompt outcomes

## Claim scope

result and evidence returned by a current Implementation Workflow prompt.

## Claim

### Prose Claim

the Implementation **must** return only a result label admitted by its current Step plus actual outputs, input/source bindings, retained state, evidence references, and blockers; absent or unperformed checks never become a passing result.

## Details

An initial expected failing Evaluation consumes zero retries. Diagnosis, retry admission, repair, and renewed checking retain real state; a repair does not imply success. Method learning remains a separate CA-O-102 Workflow.
