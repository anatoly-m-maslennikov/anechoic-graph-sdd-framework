---
atom_id: CA-E-441
ref_id: CA-E-441
container:
  scope_unit: CA-SU-13
role: Evaluation
form: Eval Policy
topics:
  main_subject: 'ANECHOIC_STRUCTURE <+ Atom/(.Header.Context.Role := Operations)/(.Header.Context.Form := Action)//Implementation Retry Control'
  dependencies:
  - ANECHOIC_MODEL <+ Entity/Object/Continuant/Actor/Operator
  - ANECHOIC_MODEL <+ Atom/(.Header.Context.Role := Evaluation)
  - "ANECHOIC_STRUCTURE <+ Aspects <+ Engineering <+ Operation <+ Execution Control <+ Failure Handling"
  - 'ANECHOIC_MODEL <+ Atom/(.Header.Context.Role := Plan).Autonomous Confidence Threshold'
  - ANECHOIC_MODEL <+ Project
  - ANECHOIC_MODEL <+ Entity/Object/Occurrent/Execution/Workflow Run.Implementation Retry Limit
tier: 6
relations:
  child_of:
  - CA-E-001
  evaluation_for:
  - CA-O-024
  - CA-O-016
  - CA-R-1559
  - CA-M-295
status: Active
version: 35
updated_at: 2026-11-02 18:35:20 +0400
current_scope_unit: PROJECT_CONFIGURATION
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-13_LAYER_3_PROJECT_CONFIGURATION/06_evaluation/CA-E-441-PROJECT_CONFIGURATION-POLICY--evaluate-retry-budget-and-escalation.md
  source_atom_id: CA-E-441
  source_atom_revision: 35
  source_sha256: 28f3eb91e7feb1cb9d7911603173b0a842a91c2272c467ca908558e31e09e2ba
  original_relations_sha256: 52c1f0b5c3a2b439de8cfe87809ef5d2ebda914234b7522c46871c374e39bf08
---
## Summary

Evaluate retry budget **and** escalation

## Claim

### Prose Claim


the retry-policy Evaluation.


the retry-policy Evaluation **must** return `fail` **if** **any** of the following occurs:

- the initial failed Evaluation consumes a retry.
- an automatic retry exceeds the effective Implementation Retry Limit resolved under CA-M-295-CORE_META_MODEL-IMPLEMENTATION_METHOD--resolve-implementation-retry-limits-by-source-precedence **and** enforced by CA-O-024-PROJECT_CONFIGURATION-ACTION--control-implementation-retries.
- starting a permitted fix-and-evaluate round is **not** counted once, **or** checking its permission again consumes another retry.
- a changed failure set **or** automatic next loop silently resets the budget.
- the last permitted retry fails **without** pausing **and** reporting remaining failures **to** the Operator.
- retrying bypasses a confidence gate, governing-Atom approval rule, **or** additional Operator constraint.
- successful completion under CA-O-016-PROJECT_CONFIGURATION-WORKFLOW--implement-evaluations-before-required-behavior still triggers another automatic repair retry.

earlier escalation required by governing authority **must not** be rejected merely because retries remain.
