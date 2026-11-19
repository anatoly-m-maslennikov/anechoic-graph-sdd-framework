---
atom_id: CA-R-2632
ref_id: CA-R-2632
role: Requirement
form: Declaration
topics:
  main_subject: ANECHOIC_MODEL <+ Project.Settings.Authority Modes
tier: 3
status: active
version: 5
updated_at: '2026-11-13T00:36:09.570555+00:00'
container:
  scope_unit: CA-SU-11
destination:
  file:
    name: CA-R-2632-CORE_META_MODEL-DECLARATION--declare-project-settings-authority-modes.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2632-CORE_META_MODEL-DECLARATION--declare-project-settings-authority-modes.md
  source_atom_id: CA-R-2632
  source_atom_revision: 5
  source_sha256: 9a862e5c26718db2e28364d778cb1e210f636a316bbf831f060f3d2ecc9179e8
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Declare Project.Settings.Authority Modes

## Claim

### Prose Claim

When authored, Project Authority Mode and Default Scope Unit Authority Mode are both required. Each value is `strict` or `casual`.

### Formal Claim

```python
from anechoic.formal_claims import Cardinality, declare_entity

declare_entity(
    entity_name="Authority Modes",
    relation_name="IS_PROPERTY_OF",
    base_path="Project.Settings",
    property_occurrence_cardinality=Cardinality(minimum=0, maximum=1),
    value_cardinality=0,
    dependent_property_cardinality=2,
    allowed_dependent_property_names=("Default Scope Unit Authority Mode", "Project Authority Mode"),
    dependent_property_value_format=str,
)
```
