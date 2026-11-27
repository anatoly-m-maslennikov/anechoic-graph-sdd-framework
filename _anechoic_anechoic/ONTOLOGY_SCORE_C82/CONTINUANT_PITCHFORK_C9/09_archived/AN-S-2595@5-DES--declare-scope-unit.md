---
atom_family: SPEC
atom_id: AN-S-2595
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 5
  updated_at: 2026-11-05 12:58:42 +0400
---

## Summary

Declare Scope Unit

## Claim

### Prose Claim

Each Scope Unit except a Project and the predefined CA-SU--1 has exactly one Scope Unit container.

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
