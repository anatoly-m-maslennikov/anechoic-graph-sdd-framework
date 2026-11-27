---
atom_family: SPEC
atom_id: AN-S-3
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
    component_id='C3', name='Example'))
```

## Component Boundaries

```python
{'io': {'server': {'worker': {'transport': 'in_process', 'entry': 'worker.run'}}}}
```

## Component Contract

```python trace
declare_trace_contract(action='run', output='ready', must_effect=(('C3', 'called'),), interface='worker', transport='in_process')
```
