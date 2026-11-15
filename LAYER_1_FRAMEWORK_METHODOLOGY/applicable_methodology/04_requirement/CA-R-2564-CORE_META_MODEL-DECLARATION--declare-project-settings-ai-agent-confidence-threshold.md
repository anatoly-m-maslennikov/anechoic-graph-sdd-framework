---
atom_id: CA-R-2564
ref_id: CA-R-2564
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: CAPRMEDIO_MODEL <+ Project.Settings.AI Agent Confidence Threshold
tier: 3
status: active
version: 5
updated_at: '2026-11-13T03:59:30.052668+00:00'
carrier_destination:
  file:
    name: CA-R-2564-CORE_META_MODEL-DECLARATION--declare-project-settings-ai-agent-confidence-threshold.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
projection:
  source_carrier_path: ../../../.caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2564-CORE_META_MODEL-DECLARATION--declare-project-settings-ai-agent-confidence-threshold.md
  source_atom_id: CA-R-2564
  source_atom_revision: 5
  source_sha256: 46f669f4036a974ee00681cc4b1d1b3f44cdedeca0627e19a2cbc6c1b8de24cc
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Declare Project.Settings.AI Agent Confidence Threshold

## Claim

### Formal Claim

```python
from caprmedio.formal_claims import declare_entity

declare_entity(
    entity_name="AI Agent Confidence Threshold",
    relation_name="IS_PROPERTY_OF",
    base_path="Project.Settings",
    property_occurrence_cardinality=1,
    value_format=int,
    value_cardinality=1,
    dependent_property_cardinality=0,
    minimum_value=0,
    maximum_value=100,
    fallback_value=90,
)
```

