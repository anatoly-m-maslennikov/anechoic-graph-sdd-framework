---
atom_id: CA-R-2963
ref_id: CA-R-2963
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: CAPRMEDIO_MODEL <+ Workflow.Content.Claim.Prose Claim
tier: 3
status: active
version: 2
updated_at: '2026-11-12T17:23:54+00:00'
carrier_destination:
  file:
    name: CA-R-2963-CORE_META_MODEL-DECLARATION--declare-workflow-content-claim-prose-claim.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
projection:
  source_carrier_path: ../../../.caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2963-CORE_META_MODEL-DECLARATION--declare-workflow-content-claim-prose-claim.md
  source_atom_id: CA-R-2963
  source_atom_revision: 2
  source_sha256: 5401343365aeff1e0bac104cf5a5f252e2bb5b7b4bcb0cd6b02a2123deb9ebcf
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---

## Summary

Declare Workflow.Content.Claim.Prose Claim

## Claim

### Formal Claim

```python
# model
from caprmedio.formal_claims import Cardinality, declare_entity

declare_entity(
    entity_name='Prose Claim',
    relation_name='IS_PROPERTY_OF',
    base_path='Workflow.Content.Claim',
    property_occurrence_cardinality=Cardinality(minimum=0, maximum=1),
    value_cardinality=1,
    value_format='markdown',
    dependent_property_cardinality=0,
)
```
