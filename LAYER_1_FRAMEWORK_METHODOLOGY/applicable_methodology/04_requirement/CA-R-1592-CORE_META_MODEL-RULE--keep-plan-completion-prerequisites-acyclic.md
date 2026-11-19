---
atom_id: CA-R-1592
ref_id: CA-R-1592
container:
  scope_unit: CA-SU-11
role: Requirement
form: Rule
topics:
  main_subject: ANECHOIC_MODEL <+ Atom/(.Header.Context.Role := Plan)
  dependencies:
  - ANECHOIC_MODEL <+ Atom/(.Header.Context.Role := Plan)
  - 'ANECHOIC_MODEL <+ Atom/(.Header.Context.Role := Plan).Header.State.Status: Done'
tier: 2
status: Active
version: 23
updated_at: 2026-11-02 00:18:22 +0400
carrier_destination:
  file:
    name: CA-R-1592-CORE_META_MODEL-RULE--keep-plan-completion-prerequisites-acyclic.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-1592-CORE_META_MODEL-RULE--keep-plan-completion-prerequisites-acyclic.md
  source_atom_id: CA-R-1592
  source_atom_revision: 23
  source_sha256: aacdcaadb7e8dad824089070e8c89438ab2c82579cdf1d0134295104ca60cc78
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Keep Plan completion prerequisites acyclic

## Claim

### Prose Claim


Plan execution.


Plan execution **must not** contain a cycle of completion prerequisites, including one formed jointly by `BLOCKS` **and** the requirement **to** complete directly contained Plan work **before** its containing Plan can be Done **or** Canceled.
