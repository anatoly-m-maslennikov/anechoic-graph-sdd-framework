---
atom_id: CA-R-2772
ref_id: CA-R-2772
container:
  scope_unit: CA-SU-11
role: Requirement
form: Rule
topics:
  main_subject: CAPRMEDIO_MODEL <+ Format
tier: 1
status: active
version: 3
updated_at: '2026-11-13T05:35:46.745468+00:00'
carrier_destination:
  file:
    name: CA-R-2772-CORE_META_MODEL-RULE--cfel-format-constraint-intersection.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
projection:
  source_carrier_path: ../../../.caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2772-CORE_META_MODEL-RULE--cfel-format-constraint-intersection.md
  source_atom_id: CA-R-2772
  source_atom_revision: 3
  source_sha256: 7bd903bd7da8321844ee07dee93a41fb7d87f9dcf45cfd91892e8b80a6197215
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

CFEL Format constraint intersection

## Claim

### Prose Claim

A comma inside one square-bracket value Format annotation combines constraints by intersection. Each direct value must satisfy every listed constraint. Thus `[int, 0..100]` admits integer values from 0 through 100 inclusive. An empty or incompatible intersection admits no values. Existing curly-brace occurrence and value-cardinality annotations keep their current meanings and remain independent.

## Details

```text
p:: [int, 0..100]{:value count}
```
