---
identity:
  atom_id: AN-S-2015
context:
  container:
    component: C9
  tier: 3
  lens: DES
state:
  status: draft
  version: 4
  updated_at: 2026-11-05 12:58:42 +0400
---

## Summary

Declare Project

## Claim

### Prose Claim


A Project uses ANECHOIC's MODEL.


### Formal Claim

```python
# model
subject_path(address='Scope Unit/Project')
classify(address='Project', axis='Container', value='yes', grouped=True)
relation(source='Project', name='NARROWER_THAN', target='Scope Unit')
# instances
population(address='Scope Unit/Project//$scope_unit', count='1')
relation(source='Project//$project', name='IS_CONTAINED_BY', target='Scope Unit//$scope_unit_2', source_count='0')
set_value(address='Project//$project_2.order.ordered', value=False)
property_rule(address='Project//$project_3.order.number', value_format='', values='0')
```

## Semantics

A Project is the root Scope Unit. The Project is not renamed or moved through Scope Unit operations. It has a stable Scope Unit ID. The shared model makes it Unordered with no order.number; individual Project Declarations inherit these facts.
