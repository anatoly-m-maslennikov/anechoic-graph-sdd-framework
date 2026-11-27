---
atom_family: SPEC
atom_id: AN-S-1
container: {component: C1}
tier: 1
context: {template: component_manifest}
relations: {}
state: {status: active, version: 1}
---

## Summary

Declare the Component.

## Purpose

Model one public Action.

## Component Identity

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest
declare_entity(entity_name='Component Manifest', instance=ComponentManifest(
    component_id='C2', name='Example'))
```

## Component Boundaries

```python
{'io': {'client': {'worker': {'component': 'C3', 'transport': 'in_process'}}}}
```

## Component Contract

```python trace
declare_trace_contract(action='run', output='ready', must_effect=(('C3', 'called'),))
```
