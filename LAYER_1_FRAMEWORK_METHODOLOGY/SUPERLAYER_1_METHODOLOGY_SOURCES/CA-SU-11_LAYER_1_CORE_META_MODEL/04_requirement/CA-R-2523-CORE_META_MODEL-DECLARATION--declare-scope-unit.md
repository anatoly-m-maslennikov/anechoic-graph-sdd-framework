---
atom_id: CA-R-2523
ref_id: CA-R-2523
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: ANECHOIC_MODEL <+ Scope Unit
tier: 3
status: active
version: 6
updated_at: '2026-11-13T22:57:24.985880+00:00'
carrier_destination:
  file:
    name: CA-R-2523-CORE_META_MODEL-DECLARATION--declare-scope-unit.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
---


## Summary

Declare Scope Unit

## Claim

### Prose Claim

Each Scope Unit other than a Project and CA-SU--1 has exactly one IS_CONTAINED_BY link to a Scope Unit.

### Formal Claim

```python
from anechoic.formal_claims import Cardinality, declare_entity
from anechoic.model import Continuant

class ScopeUnit(Continuant):
    pass

declare_entity(
    entity_name="Scope Unit",
    entity_class=ScopeUnit,
    classifications={"Container": "yes"},
    instance_relation_constraints={
        "CONTAINS": {
            "target_entity_paths": ("Atom", "Scope Unit"),
            "targets_per_source": Cardinality(minimum=0, maximum=None),
        },
        "IS_CONTAINED_BY": {
            "target_entity_paths": ("Scope Unit",),
            "targets_per_source": Cardinality(minimum=0, maximum=1),
        },
    },
)
```

## Semantics

A Scope Unit defines a boundary of responsibility for Atoms.
