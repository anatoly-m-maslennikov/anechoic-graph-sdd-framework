---
atom_id: CA-R-2759
ref_id: CA-R-2759
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: ANECHOIC_MODEL <+ External Remote Runtime
tier: 3
status: active
version: 1
updated_at: 2026-11-04 16:07:35 +0400
carrier_destination:
  file:
    name: CA-R-2759-CORE_META_MODEL-DECLARATION--declare-external-remote-runtime.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2759-CORE_META_MODEL-DECLARATION--declare-external-remote-runtime.md
  source_atom_id: CA-R-2759
  source_atom_revision: 1
  source_sha256: 83fca4f475409c14e208fe8f7127cb8b94ec2461d5bcfc7d68567ce7df3be180
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Declare External Remote Runtime

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Runtime

class ExternalRemoteRuntime(Runtime):
    pass

declare_entity(
    entity_class=ExternalRemoteRuntime,
    entity_name='External Remote Runtime',
)
```

## Semantics

An External Remote Runtime is a Runtime external to our application on a machine other than the Operator’s.
