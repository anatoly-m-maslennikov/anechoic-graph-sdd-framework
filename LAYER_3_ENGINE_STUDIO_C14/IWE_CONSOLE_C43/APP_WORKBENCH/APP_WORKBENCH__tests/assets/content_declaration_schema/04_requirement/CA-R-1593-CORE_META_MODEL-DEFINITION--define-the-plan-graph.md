---
atom_id: CA-R-1593
ref_id: CA-R-1593
container:
  scope_unit: CA-SU-11
role: Requirement
form: Rule
topics:
  main_subject: ANECHOIC_MODEL <+ Projection
  dependencies:
  - 'ANECHOIC_MODEL <+ Atom/(.Header.Context.Role := Plan)/(.Header.Context.Form := Plan)'
  - ANECHOIC_MODEL <+ Projection
  - ANECHOIC_MODEL <+ Relation
  - ANECHOIC_MODEL <+ Carrier
tier: 1
status: Active
version: 25
updated_at: 2026-11-02 00:18:22 +0400
carrier_destination:
  file:
    name: CA-R-1593-CORE_META_MODEL-RULE--define-the-plan-graph.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
---
## Summary

Define the Plan Graph

## Claim

### Prose Claim


the Plan Graph.


the Plan Graph **means** a Projection whose nodes reference authoritative Plan Atoms **and** whose graph-owned Relations represent Plan containment **and** blocking. explicit once-owned Plan Relation declarations are the sources of those facts; optional directory placement represents them **without** becoming another declaration.
