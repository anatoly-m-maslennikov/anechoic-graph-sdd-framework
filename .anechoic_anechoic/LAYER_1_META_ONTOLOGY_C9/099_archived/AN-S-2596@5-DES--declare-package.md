---
identity:
  atom_id: AN-S-2596
context:
  container:
    component: C9
  tier: 3
  lens: DES
state:
  status: archived
  version: 5
  updated_at: '2026-11-13T22:57:24.985880+00:00'
---

## Summary

Declare Package

## Claim

### Prose Claim

Each Package other than a Project Package has exactly one IS_CONTAINED_BY link to a Package.

### Formal Claim

```python
from anechoic.formal_claims import Cardinality, declare_entity
from anechoic.model import Continuant

class Package(Continuant):
    pass

declare_entity(
    entity_name="Package",
    entity_class=Package,
    classifications={"Container": "yes"},
    instance_relation_constraints={
        "CONTAINS": {
            "target_entity_paths": ("Package",),
            "targets_per_source": Cardinality(minimum=0, maximum=None),
        },
        "IS_CONTAINED_BY": {
            "target_entity_paths": ("Package",),
            "targets_per_source": Cardinality(minimum=0, maximum=1),
        },
    },
)
```

## Semantics

A logical collection of implementation and documentation parts.
