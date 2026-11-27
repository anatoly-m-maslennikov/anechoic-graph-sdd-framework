---
atom_family: SPEC
atom_id: AN-S-2
container: {component: C2}
tier: 0
context: {template: solution}
relations: {ANSWERS: [AN-S-1@1]}
state: {status: active, version: 1}
---

## Claim

### Formal Claim

```python
component_workflow(component='C2', action='run', machine={
    'id': 'run', 'initial': 'start', 'states': {
        'start': {'on': {'start': {'target': 'running', 'guard': {'type': 'matchesTrace',
            'params': {'kind': 'trigger'}}}}},
        'running': {'on': {'invoke': {'target': 'returning', 'guard': {'type': 'matchesTrace',
            'params': {'kind': 'effect', 'target': 'C3', 'outcome': 'called', 'detail': {'component': 'C3', 'action': 'run', 'output': 'ready', 'interface': 'worker', 'transport': 'in_process', 'entry': 'worker.run', 'manifest': 'AN-S-3@1'}}}}}},
        'returning': {'on': {'return': {'target': 'done', 'guard': {'type': 'matchesTrace',
            'params': {'kind': 'output', 'outcome': 'ready'}}}}},
        'done': {'type': 'final'}}})
```
