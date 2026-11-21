---
atom_family: SPEC
atom_id: AN-S-2015
structure:
  container:
    component: C9
  tier: 3
context:
  lens: DES
state:
  status: archived
  version: 7
  updated_at: '2026-11-12T12:33:04.158402+00:00'
---

## Summary

Declare Project

## Claim

### Prose Claim

A Project uses ANECHOIC's MODEL.

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ScopeUnit

class Project(ScopeUnit):
    pass

declare_entity(
    entity_class=Project,
    entity_name='Project',
    classifications={'Container': 'yes'},
    instance_population_cardinality=1,
    instance_population_scope='project',
    instance_relation_constraints={'IS_CONTAINED_BY': {'target_entity_paths': ('Scope Unit',), 'targets_per_source': 0}},
    required_instance_property_values={'order.ordered': False},
    instance_property_constraints={'order.number': {'value_cardinality': 0}},
)
```

## Semantics

A Project is the root Scope Unit. It is not renamed or moved through Scope Unit operations. Its one stable Scope Unit ID is governed by CA-R-2526. The shared model makes Project unordered with no order.number; individual Project Declarations inherit these facts.
