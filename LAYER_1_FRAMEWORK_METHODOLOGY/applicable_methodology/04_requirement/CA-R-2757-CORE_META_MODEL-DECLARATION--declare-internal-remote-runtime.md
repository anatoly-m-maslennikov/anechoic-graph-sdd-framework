---
atom_id: CA-R-2757
ref_id: CA-R-2757
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: CAPRMEDIO_MODEL <+ Internal Remote Runtime
tier: 3
status: active
version: 1
updated_at: 2026-11-04 16:07:35 +0400
carrier_destination:
  file:
    name: CA-R-2757-CORE_META_MODEL-DECLARATION--declare-internal-remote-runtime.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
projection:
  source_carrier_path: ../../../.caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2757-CORE_META_MODEL-DECLARATION--declare-internal-remote-runtime.md
  source_atom_id: CA-R-2757
  source_atom_revision: 1
  source_sha256: 2685839837021e13c778ee07b25aab52c1558789144ad9860ffca4bd79d93854
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Declare Internal Remote Runtime

## Claim

### Formal Claim

```python
from caprmedio.formal_claims import declare_entity
from caprmedio.model import Runtime

class InternalRemoteRuntime(Runtime):
    pass

declare_entity(
    entity_class=InternalRemoteRuntime,
    entity_name='Internal Remote Runtime',
)
```

## Semantics

An Internal Remote Runtime is a Runtime of our application on a machine other than the Operator’s.
