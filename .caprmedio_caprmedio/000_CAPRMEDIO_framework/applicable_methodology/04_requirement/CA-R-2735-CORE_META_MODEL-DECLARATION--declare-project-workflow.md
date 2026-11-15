---
atom_id: CA-R-2735
ref_id: CA-R-2735
role: Requirement
form: Declaration
topics:
  main_subject: CAPRMEDIO_MODEL <+ Atom/(.Header.Context.Role := Operations)/Workflow/(.Purpose
    := Project)
tier: 3
status: active
version: 4
updated_at: '2026-11-13T03:39:10.851210+00:00'
container:
  scope_unit: CA-SU-11
destination:
  file:
    name: CA-R-2735-CORE_META_MODEL-DECLARATION--declare-project-workflow.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
projection:
  source_carrier_path: ../../../.caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2735-CORE_META_MODEL-DECLARATION--declare-project-workflow.md
  source_atom_id: CA-R-2735
  source_atom_revision: 4
  source_sha256: 3c126f02f375e3c183eea633a9f78743fb53a66ff98c65de293556a89a03ad69
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---

## Summary

Declare Project Workflow

## Claim

### Formal Claim

```python
from caprmedio.formal_claims import declare_entity

declare_entity(
    entity_name="Purpose",
    relation_name="IS_PROPERTY_OF",
    base_path="Atom/(.Header.Context.Role := Operations)/Workflow",
    allowed_values=('Project',),
)
```

## Semantics

A Project Workflow is a Workflow whose Purpose is Project: it develops, validates, maintains or releases a Project's result. Examples include Implementation, Local Release and Public Release.

It inherits Workflow's shared recursive Step and Action model. Purpose describes use relative to a Project and does not change the canonical definition's owning Scope Unit.
