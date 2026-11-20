---
atom_family: SPEC
atom_id: AN-S-2171
structure:
  container:
    component: C9
  tier: 3
context:
  lens: DES
state:
  status: active
  version: 3
  updated_at: '2026-11-12T23:57:56.938436+00:00'
---

## Summary

Declare Journal

## Claim

### Formal Claim

```python
from anechoic.formal_claims import Cardinality, declare_entity
from anechoic.model import Continuant

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
