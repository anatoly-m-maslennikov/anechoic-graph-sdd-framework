---
atom_id: CA-R-1979
ref_id: CA-R-1979
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: ANECHOIC_MODEL <+ Project.Settings.Confidence
tier: 3
relations:
  child_of:
  - CA-R-1176
status: active
version: 17
updated_at: '2026-11-12T17:23:54+00:00'
carrier_destination:
  file:
    name: CA-R-1979-CORE_META_MODEL-DECLARATION--define-project-framework-settings-confidence.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-1979-CORE_META_MODEL-DECLARATION--define-project-framework-settings-confidence.md
  source_atom_id: CA-R-1979
  source_atom_revision: 17
  source_sha256: b0311ba3b68e2df59e26aa7e7ed56b7132696d33a3daf0c2c64d5f89b797e4d7
  original_relations_sha256: 9e3e53a370b31aee7f492cc3fbaba3b8b30f92b5773698d221265754db5d0402
---
## Summary

Define Project.Framework Settings.Confidence

## Claim

### Prose Claim


the Confidence grouping in the Project's Framework Settings.



### Formal Claim

```python
# model
from anechoic.formal_claims import Cardinality, declare_entity

declare_entity(
    entity_name='Confidence',
    relation_name='IS_PROPERTY_OF',
    base_path='Project.Settings',
    property_occurrence_cardinality=Cardinality(minimum=0, maximum=1),
    value_cardinality=0,
    dependent_property_cardinality=Cardinality(minimum=0, maximum=2),
    allowed_dependent_property_names=('Necessary Information Threshold', 'Semantic Resolution Threshold'),
    dependent_property_value_format='int',
)
```

## Details

Evidence: CA-R-1652 defines the necessary-information threshold default; CA-R-380 defines the semantic-resolution threshold default. These define the child settings, not the parent grouping. Candidate #6 decision 8 retains Settings as the default source, and decision 18 distinguishes Project settings from the framework's name. This grouping adds no threshold, override layer or mandatory value. Concrete ANECHOIC setting definitions belong in Project Configuration.
