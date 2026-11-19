---
atom_id: CA-R-2626
ref_id: CA-R-2626
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: ANECHOIC_MODEL <+ Project.Settings.Interaction.Reporting Mode
tier: 3
status: active
version: 2
updated_at: '2026-11-12T17:23:54+00:00'
carrier_destination:
  file:
    name: CA-R-2626-CORE_META_MODEL-DECLARATION--define-interaction-reporting-mode.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2626-CORE_META_MODEL-DECLARATION--define-interaction-reporting-mode.md
  source_atom_id: CA-R-2626
  source_atom_revision: 2
  source_sha256: dab6357bfa97ca81cfa54fa968a5c3fc46b1445e7bbf680ed1db03c47d97db62
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---

## Summary

Define Interaction Reporting Mode

## Claim

### Formal Claim

```python
# model
from anechoic.formal_claims import declare_entity

declare_entity(
    entity_name='Reporting Mode',
    relation_name='IS_PROPERTY_OF',
    base_path='Project.Settings.Interaction',
    property_occurrence_cardinality=1,
    value_cardinality=1,
    value_format='str',
    dependent_property_cardinality=0,
)
```

