---
identity:
  ref_id: CA-E-803@5-draft
  id: CA-E-803
context:
  container:
    scope_unit: CA-SU-45
  role: Evaluation
  form: Eval Case
  topics:
    main_subject: PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation
      <+ Data Handling <+ Schema
    dependencies:
    - MODEL//ANECHOIC <+ Relation
  tier: 7
relations:
  evaluation_for:
  - CA-R-2724
  - CA-M-509
  IS_REPLACEMENT_FOR:
  - CA-E-803
state:
  status: draft
  version: 5
  updated_at: '2026-11-13T22:33:00.097252+00:00'
destination:
  file:
    name: CA-E-803@5-draft-WORKBENCH_BACKEND-EVAL_CASE--verify-canonical-direct-and-inverse-relation-facts.md
    path: .anechoic_anechoic/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/CA-SU-15_FEATURE_PROGRAMMATIC/CA-SU-20_FEATURE_APPS/CA-SU-43_APP_WORKBENCH/CA-SU-45_FEATURE_WORKBENCH_BACKEND/06_evaluation/000_draft
author: Anatoly Maslennikov
---
## Summary

Verify canonical direct and inverse relation facts

## Claim

### Prose Claim

#### Registry and facts

Verify Current Requirement relation Declarations, including Relation Declaration, register admitted direct facts and inverse aliases; Draft Declarations do not change the Current registry. Either authored direction materializes one canonical direct fact, swaps inverse endpoints once, and does not duplicate direct or inverse views. Exact model addresses are required; unique case-folding applies only to carrier keys.

Verify container facts use effective Header.Container and the Project root resolves to `uppercase(Project prefix)-SU-00`. Ambiguous names, inverse metadata or case-colliding native labels warn and omit affected facts and bindings without choosing a winner. Unrelated facts and source bytes stay unchanged. Prose, general CFEL and qualified derivations are never runtime facts.

#### Refresh and parity

Verify create, edit, move, rename, delete, invalidate and repair refresh affected direct and inverse facts and hashes. Missing targets remain references; reappearance does not duplicate them. Compare single-source and multi-source final columns, traversal and hashes with a full rebuild. Unrelated edits remain incremental.
