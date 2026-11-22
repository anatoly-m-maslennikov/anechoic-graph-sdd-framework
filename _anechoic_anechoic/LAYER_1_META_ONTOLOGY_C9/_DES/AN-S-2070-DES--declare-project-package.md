---
atom_family: SPEC
atom_id: AN-S-2070
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: active
  version: 3
  updated_at: '2026-11-12T12:33:04.158402+00:00'
---

## Summary

Declare Project Package

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Package

class ProjectPackage(Package):
    pass

declare_entity(
    entity_class=ProjectPackage,
    entity_name='Project Package',
    instance_population_cardinality=1,
    instance_population_scope='project',
    instance_relation_constraints={'IS_CONTAINED_BY': {'target_entity_paths': ('Package',), 'targets_per_source': 0}},
)
```

## Semantics

The Project Package is the root Package of a Project's implementation.
