---
atom_id: CA-R-2733
ref_id: CA-R-2733
role: Requirement
form: Declaration
topics:
  main_subject: CAPRMEDIO_MODEL <+ Atom/(.Header.Context.Role := Operations)/Workflow.Purpose
tier: 3
status: active
version: 3
updated_at: '2026-11-13T00:03:26.251582+00:00'
container:
  scope_unit: CA-SU-11
destination:
  file:
    name: CA-R-2733-CORE_META_MODEL-DECLARATION--declare-workflow-purpose.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
projection:
  source_carrier_path: ../../../.caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2733-CORE_META_MODEL-DECLARATION--declare-workflow-purpose.md
  source_atom_id: CA-R-2733
  source_atom_revision: 3
  source_sha256: ea823ff146578403f2baf79ac9118bd08e62c834e765ededa498f8c9c882829b
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---


## Summary

Declare Workflow.Purpose

## Claim

### Formal Claim

```python
from caprmedio.formal_claims import declare_entity

declare_entity(
    entity_name="Purpose",
    relation_name="IS_PROPERTY_OF",
    base_path="Atom/(.Header.Context.Role := Operations)/Workflow",
    value_format=str,
    value_cardinality=1,
)
```
