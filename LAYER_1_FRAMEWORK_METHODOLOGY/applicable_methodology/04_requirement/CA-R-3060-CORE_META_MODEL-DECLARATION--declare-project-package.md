---
atom_id: CA-R-3060
ref_id: CA-R-3060
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: CAPRMEDIO_MODEL <+ Package/Project Package
tier: 3
status: active
version: 3
updated_at: '2026-11-12T12:33:04.158402+00:00'
carrier_destination:
  file:
    name: CA-R-3060-CORE_META_MODEL-DECLARATION--declare-project-package.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
relations:
  is_replacement_for:
  - CA-R-2553
projection:
  source_carrier_path: ../../../.caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-3060-CORE_META_MODEL-DECLARATION--declare-project-package.md
  source_atom_id: CA-R-3060
  source_atom_revision: 3
  source_sha256: 47612fe2df35d717846cbbd3e7b98ef21f8a02c328f45050b2de83d352001375
  original_relations_sha256: db393ca5c05c09d7410fed3bb77c55fea66a2bc46986cfa5585536b1fae282a7
---

## Summary

Declare Project Package

## Claim

### Formal Claim

```python
from caprmedio.formal_claims import declare_entity
from caprmedio.model import Package

class ProjectPackage(Package):
    pass

declare_entity(
    entity_class=ProjectPackage,
    entity_name='Project Package',
    instance_population_cardinality=1,
    instance_population_scope='project',
    instance_relation_constraints={'IS_CONTAINED_BY': {'target_entity_paths': ('Package',), 'targets_per_source': 0}},
)
```

## Semantics

The Project Package is the root Package of a Project's implementation.
