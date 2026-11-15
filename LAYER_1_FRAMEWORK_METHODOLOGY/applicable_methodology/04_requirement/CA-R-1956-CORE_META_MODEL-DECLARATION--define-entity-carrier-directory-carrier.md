---
atom_id: CA-R-1956
ref_id: CA-R-1956
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: CAPRMEDIO_MODEL <+ Carrier/Directory
tier: 3
relations:
  child_of:
  - CA-R-1174
status: active
version: 14
updated_at: '2026-11-12T17:23:54+00:00'
carrier_destination:
  file:
    name: CA-R-1956-CORE_META_MODEL-DECLARATION--define-entity-carrier-directory-carrier.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-1956-CORE_META_MODEL-DECLARATION--define-entity-carrier-directory-carrier.md
  source_atom_id: CA-R-1956
  source_atom_revision: 14
  source_sha256: 06f55d04d25a5c949ebeb98532f9d297a4204c332e60e6c6c5cfd021bffccc04
  original_relations_sha256: 2e54810b23dc6829999889d9dce55018a30d8606de806fb64b6f8578b2c66336
---
## Summary

Define Entity/Carrier/Directory Carrier

## Claim

### Prose Claim

A Directory Carrier uses a directory to represent its carried Object; containing files alone does not make it a Directory Carrier.
### Formal Claim

```python
from caprmedio.formal_claims import declare_entity
from caprmedio.model import Carrier

class Directory(Carrier):
    pass

declare_entity(entity_class=Directory, entity_name='Directory')
```

