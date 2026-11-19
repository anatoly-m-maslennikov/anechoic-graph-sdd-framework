---
atom_id: CA-R-2771
ref_id: CA-R-2771
container:
  scope_unit: CA-SU-11
role: Requirement
form: Rule
topics:
  main_subject: ANECHOIC_MODEL <+ Format
tier: 1
status: active
version: 3
updated_at: '2026-11-13T05:35:43.598645+00:00'
carrier_destination:
  file:
    name: CA-R-2771-CORE_META_MODEL-RULE--cfel-numeric-range-constraint.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2771-CORE_META_MODEL-RULE--cfel-numeric-range-constraint.md
  source_atom_id: CA-R-2771
  source_atom_revision: 3
  source_sha256: 465c32a7d3782478ade100f4b022fdec34b38c4a53fc1d5b43b2d58469db5238
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

CFEL numeric range constraint

## Claim

### Prose Claim

Inside a square-bracket value Format annotation, `lower..upper` is a closed numeric interval: both endpoints are included. It constrains each direct Property value and does not state Property occurrence or value cardinality. This square-bracket value constraint is distinct from the existing curly-brace cardinality range `{:n..m}`.

## Details

```text
p:: [0..100]{:value count}
```
