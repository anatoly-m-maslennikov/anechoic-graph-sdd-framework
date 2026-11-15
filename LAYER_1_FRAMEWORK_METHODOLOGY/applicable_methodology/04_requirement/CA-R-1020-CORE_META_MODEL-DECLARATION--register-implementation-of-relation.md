---
atom_id: CA-R-1020
ref_id: CA-R-1020
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: CAPRMEDIO_MODEL <+ Relation//implementation_of
  dependencies:
  - CAPRMEDIO_MODEL <+ Relation
tier: 1
status: active
version: 34
updated_at: '2026-11-12T17:23:54+00:00'
carrier_destination:
  file:
    name: CA-R-1020-CORE_META_MODEL-DECLARATION--register-implementation-of-relation.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
projection:
  source_carrier_path: ../../../.caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-1020-CORE_META_MODEL-DECLARATION--register-implementation-of-relation.md
  source_atom_id: CA-R-1020
  source_atom_revision: 34
  source_sha256: ec57150346480b34629d742957368cd1ef960c697b63a9892a6692395fe9f658
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Register implementation_of relation

## Claim

### Prose Claim

implementation_of is the direct Relation owned by a governed Implementation Carrier. The Host is that governed Implementation Carrier and each tuple targets the specification Atom it implements.

### Formal Claim

```python
from caprmedio.formal_claims import declare_relation

declare_relation(
    relation_name='implementation_of',
    source_endpoint={'level': 'instances', 'entity_paths': ('Carrier',)},
    target_endpoint={'level': 'instances', 'entity_paths': ('Atom',)},
)
```

