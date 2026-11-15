---
identity:
  id: CA-R-3074
  ref_id: CA-R-3074
context:
  container:
    scope_unit: CA-SU-11
  role: requirement
  form: declaration
  topics:
    main_subject: CAPRMEDIO_MODEL <+ Atom/(.Header.Context.Role := Plan).Header.Context.Plan
  tier: 3
state:
  status: active
  version: 2
  updated_at: '2026-11-12T19:20:13.431957+00:00'
destination:
  file:
    name: CA-R-3074-CORE_META_MODEL-DECLARATION--declare-atom-header-context-role-plan-header-context-plan.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
projection:
  source_carrier_path: ../../../.caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-3074-CORE_META_MODEL-DECLARATION--declare-atom-header-context-role-plan-header-context-plan.md
  source_atom_id: CA-R-3074
  source_atom_revision: 2
  source_sha256: 20ada18c7b1de0cda9810638fafbfb1ae4e5f937286018dd4635df0dcb28fde1
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---

## Summary

Declare Atom/(.Header.Context.Role := Plan).Header.Context.Plan

## Claim

### Prose Claim

The Plan group is present only for an Atom with Plan Role and is omitted when it would contain no declared Property.

### Formal Claim

```python
from caprmedio.formal_claims import Cardinality, declare_entity
from caprmedio.model import Plan

declare_entity(
    entity_name='Plan',
    relation_name="IS_PROPERTY_OF",
    base_path='Atom.Header.Context',
    property_occurrence_cardinality=Cardinality(minimum=0, maximum=1),
    value_cardinality=0,
    dependent_property_cardinality=Cardinality(minimum=1, maximum=2),
    allowed_dependent_property_names=('Work Sequence Number', 'AI Agent Confidence Threshold'),
    applies_to_entity_classes=(Plan,),
)
```
