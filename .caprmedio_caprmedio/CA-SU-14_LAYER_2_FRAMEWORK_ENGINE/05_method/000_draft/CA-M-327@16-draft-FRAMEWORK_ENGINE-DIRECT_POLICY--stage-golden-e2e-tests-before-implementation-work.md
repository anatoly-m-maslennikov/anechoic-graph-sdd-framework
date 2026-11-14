---
atom_id: CA-M-327
ref_id: CA-M-327@16-draft
container:
  scope_unit: CA-SU-14
role: Method
form: Direct Policy
topics:
  main_subject: PROJECT STRUCTURE//CAPRMEDIO <+ Aspects <+ Engineering <+ Quality
    <+ Verification <+ Test Design
  dependencies:
  - PROJECT STRUCTURE//CAPRMEDIO <+ Aspects <+ Engineering <+ Development <+ Authoring
    <+ Prompt Authoring
  - MODEL//CAPRMEDIO <+ Atom/(.Header.Context.Role := Evaluation)
tier: 3
status: draft
version: 16
updated_at: '2026-11-14T08:20:31.762668+00:00'
carrier_destination:
  file:
    name: CA-M-327@16-draft-FRAMEWORK_ENGINE-DIRECT_POLICY--stage-golden-e2e-tests-before-implementation-work.md
    path: .caprmedio_caprmedio/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/05_method/000_draft
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

For a bounded implementation packet, prepare executable golden E2E cases
from Evaluation authority and a runnable baseline before implementing
admitted R/D behavior. Run the selected checks after implementation.

## Details

- Mock only external boundaries. Exercise the behavior under test.
- A baseline or expected initial failure proves test preparation only.
