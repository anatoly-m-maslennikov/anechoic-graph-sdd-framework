---
identity:
  id: CA-R-3071
  ref_id: CA-R-3071
context:
  container:
    scope_unit: CA-SU-11
  role: requirement
  form: declaration
  topics:
    main_subject: ANECHOIC_MODEL <+ Atom.Header.Identity
  tier: 3
state:
  status: active
  version: 2
  updated_at: '2026-11-13T00:27:02.702771+00:00'
destination:
  file:
    name: CA-R-3071-CORE_META_MODEL-DECLARATION--declare-atom-header-identity.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-3071-CORE_META_MODEL-DECLARATION--declare-atom-header-identity.md
  source_atom_id: CA-R-3071
  source_atom_revision: 2
  source_sha256: 793d530744aeece0aaac15e4b79b51b2858708edb7f67095d29a54f19e6aaf26
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---


## Summary

Declare Atom.Header.Identity

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity

declare_entity(
    entity_name='Identity',
    relation_name="IS_PROPERTY_OF",
    base_path="Atom.Header",
    property_occurrence_cardinality=1,
    value_cardinality=0,
    dependent_property_cardinality=2,
    allowed_dependent_property_names=('ID', 'Ref ID'),
    ordered_dependent_property_pairs=(('ID', 'Ref ID'),),
)
```
