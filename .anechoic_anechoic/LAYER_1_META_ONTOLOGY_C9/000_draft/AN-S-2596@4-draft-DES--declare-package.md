---
atom_family: SPEC
atom_id: AN-S-2596
structure:
  container:
    component: C9
  tier: 3
context:
  lens: DES
state:
  status: draft
  version: 4
  updated_at: 2026-11-10 14:38:45 +0400
---

## Summary

Declare Package

## Claim

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
            "targets_per_source": 1,
        },
    },
)
```

## Semantics

A logical collection of implementation and documentation parts.
