---
atom_id: CA-R-1978
ref_id: CA-R-1978
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: ANECHOIC_MODEL <+ Project.Settings.Code-Root Locators
tier: 3
relations:
  child_of:
  - CA-R-1176
status: active
version: 16
updated_at: '2026-11-12T17:23:54+00:00'
carrier_destination:
  file:
    name: CA-R-1978-CORE_META_MODEL-DECLARATION--define-project-framework-settings-code-root-locators.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-1978-CORE_META_MODEL-DECLARATION--define-project-framework-settings-code-root-locators.md
  source_atom_id: CA-R-1978
  source_atom_revision: 16
  source_sha256: 60200dde55f42b60734e4b3ba10d2fe1c30cd4788211214f43e357247e191d4a
  original_relations_sha256: 9e3e53a370b31aee7f492cc3fbaba3b8b30f92b5773698d221265754db5d0402
---
## Summary

Define Project.Framework Settings.Code-Root Locators

## Claim

### Prose Claim


the code-root references in the Project's Framework Settings.



### Formal Claim

```python
# model
from anechoic.formal_claims import Cardinality, declare_entity

declare_entity(
    entity_name='Code-Root Locators',
    relation_name='IS_PROPERTY_OF',
    base_path='Project.Settings',
    property_occurrence_cardinality=Cardinality(minimum=0, maximum=1),
    value_cardinality=Cardinality(minimum=1, maximum=None),
    value_format='str',
    dependent_property_cardinality=0,
)
```

## Details

Evidence: CA-D-371 requires code-root locators in Framework Settings. Candidate #6 keeps concrete ANECHOIC mechanisms in Project Configuration. This definition adds no discovery procedure, new root or locator count.
