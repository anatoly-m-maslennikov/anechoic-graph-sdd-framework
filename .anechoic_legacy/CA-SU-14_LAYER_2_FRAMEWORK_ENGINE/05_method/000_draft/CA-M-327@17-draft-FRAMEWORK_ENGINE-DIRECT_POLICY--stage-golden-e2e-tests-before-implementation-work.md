---
atom_id: CA-M-327
ref_id: CA-M-327@17-draft
container:
  scope_unit: CA-SU-14
role: Method
form: Direct Policy
topics:
  main_subject: PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Quality
    <+ Verification <+ Test Design
  dependencies:
  - PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development <+ Authoring
    <+ Prompt Authoring
  - MODEL//ANECHOIC <+ Atom/(.Header.Context.Role := Evaluation)
tier: 3
status: draft
version: 17
updated_at: '2026-11-14T08:28:40.764732+00:00'
carrier_destination:
  file:
    name: CA-M-327@17-draft-FRAMEWORK_ENGINE-DIRECT_POLICY--stage-golden-e2e-tests-before-implementation-work.md
    path: .anechoic_anechoic/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/05_method/000_draft
current_scope_unit: FRAMEWORK_ENGINE
claim_target_scope_unit: FRAMEWORK_ENGINE
author: Anatoly Maslennikov
relations:
  IS_REPLACEMENT_FOR:
  - CA-M-327
---
## Summary
Stage golden E2E tests before implementation work

## Claim
### Prose Claim
Before implementing admitted R/D behavior, specify executable golden E2E cases from E authority and runnable baselines.
Run the selected checks after implementation.

## Details
### Scope
This applies to tests-first preparation of a selected bounded implementation packet.
Limit mocks to external boundaries.
A baseline or expected initial failure establishes preparation only.
