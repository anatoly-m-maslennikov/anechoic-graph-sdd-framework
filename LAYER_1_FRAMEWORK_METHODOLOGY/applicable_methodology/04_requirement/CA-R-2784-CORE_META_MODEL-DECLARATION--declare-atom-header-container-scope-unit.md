---
atom_id: CA-R-2784
ref_id: CA-R-2784
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: ANECHOIC_MODEL <+ Atom.Header.Context.Container.scope_unit
tier: 3
status: active
version: 2
updated_at: '2026-11-12T17:23:54+00:00'
carrier_destination:
  file:
    name: CA-R-2784-CORE_META_MODEL-DECLARATION--declare-atom-header-container-scope-unit.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2784-CORE_META_MODEL-DECLARATION--declare-atom-header-container-scope-unit.md
  source_atom_id: CA-R-2784
  source_atom_revision: 2
  source_sha256: 41372b1ce97898cb74fe31b87d03d12fdb77beb5271ecbf0fcae8d69fa5d7f2b
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---

## Summary

Declare Atom.Header.Container.scope_unit

## Claim

### Prose Claim

The value is the stable ID of the containing Scope Unit.
### Formal Claim

```python
# model
from anechoic.formal_claims import Cardinality, declare_entity

declare_entity(
    entity_name='scope_unit',
    relation_name='IS_PROPERTY_OF',
    base_path='Atom.Header.Context.Container',
    value_cardinality=Cardinality(minimum=0, maximum=1),
    value_format='str',
    dependent_property_cardinality=0,
)
```

