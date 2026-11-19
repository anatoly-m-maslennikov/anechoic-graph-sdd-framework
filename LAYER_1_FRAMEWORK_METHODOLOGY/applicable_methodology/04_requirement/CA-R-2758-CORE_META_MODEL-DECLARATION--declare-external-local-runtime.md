---
atom_id: CA-R-2758
ref_id: CA-R-2758
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: ANECHOIC_MODEL <+ External Local Runtime
tier: 3
status: active
version: 1
updated_at: 2026-11-04 16:07:35 +0400
carrier_destination:
  file:
    name: CA-R-2758-CORE_META_MODEL-DECLARATION--declare-external-local-runtime.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2758-CORE_META_MODEL-DECLARATION--declare-external-local-runtime.md
  source_atom_id: CA-R-2758
  source_atom_revision: 1
  source_sha256: 78966f45ce8008e43233a2679e1570650700c99fec0a6be5c192cf6f6ba36ea7
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Declare External Local Runtime

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Runtime

class ExternalLocalRuntime(Runtime):
    pass

declare_entity(
    entity_class=ExternalLocalRuntime,
    entity_name='External Local Runtime',
)
```

## Semantics

An External Local Runtime is a Runtime external to our application on the Operator’s machine.
