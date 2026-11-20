---
identity:
  atom_id: AN-S-2594
context:
  container:
    component: C9
  tier: 3
  lens: DES
state:
  status: draft
  version: 6
  updated_at: 2026-11-11 14:06:22 +0400
---
## Summary

Declare Atom/(.Role := Plan)

## Claim

### Prose Claim

Each Current Plan recursively contained by a Done or Canceled Plan has exactly one Status, either Done or Canceled.

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
    classifications={"Container": "yes"},
    instance_relation_constraints={
        "CONTAINS": {"target_entity_paths": ("Atom/(.Header.Context.Role:=Plan)",), "targets_per_source": Cardinality(minimum=0, maximum=None)},
        "IS_BLOCKED_BY": {"target_entity_paths": ("Atom/(.Header.Context.Role:=Plan)",), "targets_per_source": Cardinality(minimum=0, maximum=None)},
        "BLOCKS": {"target_entity_paths": ("Atom/(.Header.Context.Role:=Plan)",), "targets_per_source": Cardinality(minimum=0, maximum=None)},
    },
)
```

## Semantics

A Plan describes bounded intended work or an intended outcome.
