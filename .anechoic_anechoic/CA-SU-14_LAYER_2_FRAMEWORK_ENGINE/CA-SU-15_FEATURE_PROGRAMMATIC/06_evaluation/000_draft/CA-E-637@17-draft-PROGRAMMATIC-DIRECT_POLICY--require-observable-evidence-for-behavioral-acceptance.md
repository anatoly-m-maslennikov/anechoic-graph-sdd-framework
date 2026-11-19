---
identity:
  atom_id: CA-E-637
  ref_id: CA-E-637@17-draft
context:
  container:
    scope_unit: CA-SU-15
  role: Evaluation
  form: Direct Policy
  topics:
    main_subject: PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Quality
      <+ Verification <+ Test Design
  tier: 1
state:
  status: draft
  version: 17
  updated_at: '2026-11-14T08:28:33.018161+00:00'
destination:
  file:
    name: CA-E-637@17-draft-PROGRAMMATIC-DIRECT_POLICY--require-observable-evidence-for-behavioral-acceptance.md
    path: .anechoic_anechoic/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/CA-SU-15_FEATURE_PROGRAMMATIC/06_evaluation/000_draft
current_scope_unit: PROGRAMMATIC
claim_target_scope_unit: PROGRAMMATIC
author: Anatoly Maslennikov
relations:
  IS_REPLACEMENT_FOR:
  - CA-E-637
---
## Summary
Require observable evidence for behavioral acceptance

## Claim
### Prose Claim
Behavioral software Evaluation can support acceptance only if every declared failure predicate has at least one reproducible check.
A check must not make acceptance depend only on replaceable private Implementation structure when a semantic or public behavior boundary can expose the predicate.

## Details
### Scope
This foundational evidence boundary applies to PROGRAMMATIC components and the applicable Spec.
Apply CA-E-389 for portfolio acceptance and cost. This Atom sets no test-scope ratio.
