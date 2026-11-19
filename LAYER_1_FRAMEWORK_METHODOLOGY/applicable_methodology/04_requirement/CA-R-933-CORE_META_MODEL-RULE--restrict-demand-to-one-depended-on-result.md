---
atom_id: CA-R-933
ref_id: CA-R-933
container:
  scope_unit: CA-SU-11
role: Requirement
form: Rule
topics:
  main_subject: 'ANECHOIC_MODEL <+ Atom/(.Header.Context.Role := Requirement)/(.Header.Context.Form := Demand)'
  dependencies:
  - ANECHOIC_MODEL <+ Atom
tier: 5
relations:
  child_of:
  - CA-R-932@37
status: Active
version: 33
updated_at: 2026-11-02 00:18:22 +0400
carrier_destination:
  file:
    name: CA-R-933-CORE_META_MODEL-RULE--restrict-demand-to-one-depended-on-result.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-933-CORE_META_MODEL-RULE--restrict-demand-to-one-depended-on-result.md
  source_atom_id: CA-R-933
  source_atom_revision: 33
  source_sha256: 8304cb0e1f6301ec219f8af0b655b216c27b73a6ef23be10e05c91924cedbd16
  original_relations_sha256: c20ed3844d666cd523ff76d7355fb5c2277a21d8c1137804e80822202d14a70b
---
## Summary
Restrict Demand to one depended-on result

## Claim

### Prose Claim


Demand Atoms.


**every** Demand Atom **must** constrain **`=1`** Producer result on which its Consumer's accepted Goal depends.
