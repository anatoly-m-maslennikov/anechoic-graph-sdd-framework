---
atom_id: CA-R-1464
ref_id: CA-R-1464
container:
  scope_unit: CA-SU-11
role: Requirement
form: Rule
topics:
  main_subject: ANECHOIC_MODEL <+ Atom.Content.Summary
  dependencies:
  - ANECHOIC_MODEL <+ Atom
  - ANECHOIC_MODEL <+ Atom.Header.Identity.ID
  - ANECHOIC_MODEL <+ Atom.Content
tier: 3
status: Active
version: 22
updated_at: 2026-11-02 00:18:22 +0400
carrier_destination:
  file:
    name: CA-R-1464-CORE_META_MODEL-RULE--keep-summary-fixed-for-atom-identity.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-1464-CORE_META_MODEL-RULE--keep-summary-fixed-for-atom-identity.md
  source_atom_id: CA-R-1464
  source_atom_revision: 22
  source_sha256: b47295b9662b44b1ae3d98179d0990a0ea27e663fb4bbb635be2799824ae8e68
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Keep Summary fixed for Atom identity

## Claim

### Prose Claim


the Summary of an Atom across its Revisions.


an Atom **must** keep the Summary created with it across **all** of its Revisions. **if** its Summary needs a change, **then** it **must** be replaced by a new Atom with a new Atom ID, even **if** its Claim is unchanged.
