---
atom_family: SPEC
atom_id: AN-S-2594
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: active
  version: 14
  updated_at: '2026-11-13T22:57:24.985880+00:00'
---

## Summary

Declare Atom/(.Role := Plan)

## Claim

### Prose Claim

An Active Plan with exactly one Work Sequence Number has exactly one Container.

A Done or Canceled Plan may not recursively contain a Plan whose Status Group is Current or Backlog unless that descendant has exactly one Status in Done or Canceled.

### Formal Claim

```python
from anechoic.formal_claims import Cardinality, declare_entity
from anechoic.model import Atom

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
