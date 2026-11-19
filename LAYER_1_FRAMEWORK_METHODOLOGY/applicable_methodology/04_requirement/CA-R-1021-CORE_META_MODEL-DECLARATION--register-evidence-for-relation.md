---
atom_id: CA-R-1021
ref_id: CA-R-1021
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: ANECHOIC_MODEL <+ Relation//evidence_for
  dependencies:
  - ANECHOIC_MODEL <+ Relation
tier: 1
status: active
version: 34
updated_at: '2026-11-12T23:18:16.780674+00:00'
carrier_destination:
  file:
    name: CA-R-1021-CORE_META_MODEL-DECLARATION--register-evidence-for-relation.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-1021-CORE_META_MODEL-DECLARATION--register-evidence-for-relation.md
  source_atom_id: CA-R-1021
  source_atom_revision: 34
  source_sha256: 055a716e8edbf4462e66bcb83c6f15a3da1b90b6ead7e43815441a31326c9816
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---

## Summary

Register evidence_for relation

## Claim

### Prose Claim

evidence_for is the direct Relation owned by an evidence Carrier. The Host is that evidence Carrier and each tuple targets the Evaluation or Implementation Carrier it supports.

### Formal Claim

```python
from anechoic.formal_claims import declare_relation

declare_relation(
    relation_name='evidence_for',
    source_endpoint={'level': 'instances', 'entity_paths': ('Carrier',)},
    target_endpoint={'level': 'instances', 'entity_paths': ('Carrier',)},
)
```

