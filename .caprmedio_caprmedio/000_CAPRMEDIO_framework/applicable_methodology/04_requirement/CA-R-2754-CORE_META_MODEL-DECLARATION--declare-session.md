---
atom_id: CA-R-2754
ref_id: CA-R-2754
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: CAPRMEDIO_MODEL <+ Session
tier: 3
status: active
version: 1
updated_at: 2026-11-04 16:07:35 +0400
carrier_destination:
  file:
    name: CA-R-2754-CORE_META_MODEL-DECLARATION--declare-session.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
projection:
  source_carrier_path: ../../../.caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2754-CORE_META_MODEL-DECLARATION--declare-session.md
  source_atom_id: CA-R-2754
  source_atom_revision: 1
  source_sha256: d9904995f157de9b3265e248fa8fcdc91c128b168f4d85f3fe6107c68217fb7c
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Declare Session

## Claim

### Formal Claim

```python
from caprmedio.formal_claims import declare_entity
from caprmedio.model import ExternalRemoteRuntime

class Session(ExternalRemoteRuntime):
    pass

declare_entity(
    entity_class=Session,
    entity_name='Session',
)
```

## Semantics

A Session is an External Remote Runtime for ongoing interaction.
