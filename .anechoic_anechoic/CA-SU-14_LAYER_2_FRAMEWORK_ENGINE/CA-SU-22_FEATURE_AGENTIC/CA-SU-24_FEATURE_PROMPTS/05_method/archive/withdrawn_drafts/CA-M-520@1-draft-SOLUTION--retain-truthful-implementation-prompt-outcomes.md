---
identity:
  atom_id: CA-M-520
  ref_id: CA-M-520@1-draft
context:
  container:
    scope_unit: CA-SU-24
  role: method
  form: solution
  topics:
    main_subject: ANECHOIC_STRUCTURE <+ Aspects <+ Engineering <+ Operation <+ Execution
      Control
    dependencies:
    - ANECHOIC_STRUCTURE <+ Aspects <+ Engineering <+ Operation <+ Execution Control
      <+ Failure Handling
    - ANECHOIC_MODEL <+ Atom/(.Header.Role := Evaluation)
    - ANECHOIC_MODEL <+ Entity/Object/Occurrent/Execution/Workflow Run
    - Subject/ANECHOIC/Graph/Node/Project Model/History
  tier: 3
state:
  status: draft
  version: 1
  updated_at: 2026-11-10 11:53:32 +0400
destination:
  file:
    name: CA-M-520@1-draft-SOLUTION--retain-truthful-implementation-prompt-outcomes.md
    path: .anechoic_anechoic/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/CA-SU-22_FEATURE_AGENTIC/CA-SU-24_FEATURE_PROMPTS/05_method/draft
current_scope_unit: PROMPTS
claim_target_scope_unit: PROMPTS
author: Anatoly Maslennikov
relations:
  IS_REPLACEMENT_FOR:
  - CA-R-1846
---
## Summary

Retain truthful implementation prompt outcomes

## Claim scope

result and evidence returned by a current Implementation Workflow prompt.

## Claim

### Prose Claim

the Implementation **must** return only a result label admitted by its current Step plus actual outputs, input/source bindings, retained state, evidence references, and blockers; absent or unperformed checks never become a passing result.

## Details

An initial expected failing Evaluation consumes zero retries. Diagnosis, retry admission, repair, and renewed checking retain real state; a repair does not imply success.
