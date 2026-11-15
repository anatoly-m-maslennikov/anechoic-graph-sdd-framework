---
atom_id: CA-R-2536
ref_id: CA-R-2536
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: CAPRMEDIO_MODEL <+ Journal
tier: 3
status: active
version: 3
updated_at: '2026-11-12T23:57:56.938436+00:00'
carrier_destination:
  file:
    name: CA-R-2536-CORE_META_MODEL-DECLARATION--declare-journal.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2536-CORE_META_MODEL-DECLARATION--declare-journal.md
  source_atom_id: CA-R-2536
  source_atom_revision: 3
  source_sha256: af501a6eec14f3e4e885316ebeaffb046989c5e2fdb90cd9db1d456598097eb7
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---

## Summary

Declare Journal

## Claim

### Formal Claim

```python
from caprmedio.formal_claims import Cardinality, declare_entity
from caprmedio.model import Continuant

class Journal(Continuant):
    pass

declare_entity(
    entity_class=Journal,
    entity_name="Journal",
    model_relation_constraints={"IS_PROPERTY_OF": {"targets_per_source": 0}},
    classifications={"Container": "yes"},
    instance_population_cardinality=1,
    instance_population_scope="project",
    instance_relation_constraints={"CONTAINS": {"target_entity_paths": ("Event Record",), "targets_per_source": Cardinality(minimum=0, maximum=None)}},
)
```

## Semantics

A Journal preserves accepted event history.
