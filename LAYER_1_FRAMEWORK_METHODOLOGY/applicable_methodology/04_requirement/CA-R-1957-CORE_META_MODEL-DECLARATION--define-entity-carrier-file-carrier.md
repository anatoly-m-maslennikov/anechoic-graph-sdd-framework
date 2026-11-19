---
atom_id: CA-R-1957
ref_id: CA-R-1957
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: ANECHOIC_MODEL <+ Carrier/File
tier: 3
relations:
  child_of:
  - CA-R-1174
status: active
version: 14
updated_at: '2026-11-12T17:23:54+00:00'
carrier_destination:
  file:
    name: CA-R-1957-CORE_META_MODEL-DECLARATION--define-entity-carrier-file-carrier.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-1957-CORE_META_MODEL-DECLARATION--define-entity-carrier-file-carrier.md
  source_atom_id: CA-R-1957
  source_atom_revision: 14
  source_sha256: 2489d891a58927ba7c2e4a619beba548634d1eaf21a8890d9acb7b6ad05d7402
  original_relations_sha256: 2e54810b23dc6829999889d9dce55018a30d8606de806fb64b6f8578b2c66336
---
## Summary

Define Entity/Carrier/File Carrier

## Claim

### Prose Claim

A File Carrier represents content in a file.
### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Carrier

class File(Carrier):
    pass

declare_entity(entity_class=File, entity_name='File')
```

