---
atom_id: CA-R-2717
ref_id: CA-R-2717
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: CAPRMEDIO_MODEL <+ Atom.Header.Destination.File.Name
tier: 3
status: active
version: 4
updated_at: '2026-11-12T17:23:54+00:00'
carrier_destination:
  file:
    name: CA-R-2717-CORE_META_MODEL-DECLARATION--declare-atom-header-carrier-destination-file-name.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2717-CORE_META_MODEL-DECLARATION--declare-atom-header-carrier-destination-file-name.md
  source_atom_id: CA-R-2717
  source_atom_revision: 4
  source_sha256: 61988ad47286379762410587732d6cd67d1dc29cee72926e06e5aff25740b9ed
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Declare Atom.Header.Carrier Destination.File.Name

## Claim

### Prose Claim




Calculated full filename, including its extension.
### Formal Claim

```python
# model
from caprmedio.formal_claims import declare_entity

declare_entity(
    entity_name='Name',
    relation_name='IS_PROPERTY_OF',
    base_path='Atom.Header.Destination.File',
    value_cardinality=1,
    dependent_property_cardinality=0,
)
```

