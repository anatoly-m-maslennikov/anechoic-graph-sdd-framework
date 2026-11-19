---
atom_id: CA-R-1662
ref_id: CA-R-1662
container:
  scope_unit: CA-SU-13
role: Requirement
form: Rule
topics:
  main_subject: 'ANECHOIC_MODEL <+ Atom/(.Header.Context.Role := Evaluation).Header.Context.Form'
tier: 3
status: Active
version: 39
updated_at: 2026-11-02 19:44:26 +0400
carrier_destination:
  file:
    name: CA-R-1662-PROJECT_CONFIGURATION-RULE--register-type-values-for-evaluation-atoms.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-13_LAYER_3_PROJECT_CONFIGURATION/04_requirement
current_scope_unit: PROJECT_CONFIGURATION
claim_target_scope_unit: PROJECT_CONFIGURATION
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-13_LAYER_3_PROJECT_CONFIGURATION/04_requirement/CA-R-1662-PROJECT_CONFIGURATION-RULE--register-type-values-for-evaluation-atoms.md
  source_atom_id: CA-R-1662
  source_atom_revision: 39
  source_sha256: 27be61a6315e1d726c1bee736664256c980d093747c5a266f1cec14ae705892d
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Register Type Values for Evaluation Atoms

## Claim

### Prose Claim


internal values of `Atom/(.Header.Role := Evaluation).Header.Form`.


Policy, Eval Case, QA Case, **and** Evaluation Control **must** be registered as internal values of `Atom/(.Header.Role := Evaluation).Header.Form`.

## Details

Eval Case is defined by CA-R-2116@9. QA Case remains registered for existing Atoms pending individually evidenced migration; this registration does not require bulk reclassification. Evaluation Control remains a distinct specific Type.
