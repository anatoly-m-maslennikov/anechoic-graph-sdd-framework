---
atom_id: CA-R-2511
ref_id: CA-R-2511
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: CAPRMEDIO_MODEL <+ Atom/(.Header.Context.Role := Plan)
tier: 3
status: active
version: 14
updated_at: '2026-11-13T22:57:24.985880+00:00'
carrier_destination:
  file:
    name: CA-R-2511-CORE_META_MODEL-DECLARATION--declare-plan.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
projection:
  source_carrier_path: ../../../.caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2511-CORE_META_MODEL-DECLARATION--declare-plan.md
  source_atom_id: CA-R-2511
  source_atom_revision: 14
  source_sha256: 8d35523543068a627e9466333b88229b5228cab2a08f9bf2f118bc43110dc10d
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---

## Summary

Declare Atom/(.Role := Plan)

## Claim

### Prose Claim

An Active Plan with exactly one Work Sequence Number has exactly one Container.

A Done or Canceled Plan may not recursively contain a Plan whose Status Group is Current or Backlog unless that descendant has exactly one Status in Done or Canceled.

### Formal Claim

```python
from caprmedio.formal_claims import Cardinality, declare_entity
from caprmedio.model import Atom

class Plan(Atom):
    pass

declare_entity(
    entity_class=Plan,
    entity_name="Plan",
    qualification_property_path="Atom.Header.Context.Role",
    classifications={"Role Order Number": 3, "Container": "yes"},
    instance_relation_constraints={
        "CONTAINS": {"target_entity_paths": ("Atom/(.Header.Context.Role:=Plan)",), "targets_per_source": Cardinality(minimum=0, maximum=None)},
        "IS_BLOCKED_BY": {"target_entity_paths": ("Atom/(.Header.Context.Role:=Plan)",), "targets_per_source": Cardinality(minimum=0, maximum=None)},
        "BLOCKS": {"target_entity_paths": ("Atom/(.Header.Context.Role:=Plan)",), "targets_per_source": Cardinality(minimum=0, maximum=None)},
    },
)
```

## Semantics

A Plan describes intended work, an intended outcome or its execution record. Work Report is the Form for that execution record.
