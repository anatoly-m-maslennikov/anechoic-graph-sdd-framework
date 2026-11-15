---
atom_id: CA-R-1666
ref_id: CA-R-1666
container:
  scope_unit: CA-SU-13
role: Requirement
form: Rule
topics:
  main_subject: CAPRMEDIO_MODEL <+ Atom/(.Header.Context.Role := Plan).Header.Context.Form
  dependencies:
  - CAPRMEDIO_MODEL <+ Entity
tier: 2
status: Active
version: 37
updated_at: 2026-11-02 19:44:26 +0400
carrier_destination:
  file:
    name: CA-R-1666-PROJECT_CONFIGURATION-RULE--register-action-policy-for-plan-atoms.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-13_LAYER_3_PROJECT_CONFIGURATION/04_requirement
current_scope_unit: PROJECT_CONFIGURATION
claim_target_scope_unit: PROJECT_CONFIGURATION
projection:
  source_carrier_path: ../../../.caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-13_LAYER_3_PROJECT_CONFIGURATION/04_requirement/CA-R-1666-PROJECT_CONFIGURATION-RULE--register-action-policy-for-plan-atoms.md
  source_atom_id: CA-R-1666
  source_atom_revision: 37
  source_sha256: b57ae304f6b0ffd525674e88b58b407f79e4f8fb7fe32a486816d6df8e6f9be2
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Register Action Policy for Plan Atoms

## Claim

### Prose Claim


the CAPRMEDIO Project Configuration registration of `Atom/(.Header.Role := Plan).Header.Form` values.


the CAPRMEDIO Project Configuration **must** register Action Policy as an additional value of `Atom/(.Header.Role := Plan).Header.Form`; Plan retains its canonical admission under CA-R-1574@21-CORE_META_MODEL-DEFINITION--define-the-common-plan-atom; navigation Labels do **not** add further Type values.
