---
atom_family: SPEC
atom_id: AN-S-4
container: {component: C3}
tier: 0
context: {template: solution}
relations: {ANSWERS: [AN-S-3@1]}
state: {status: active, version: 1}
---

## Claim

### Formal Claim

```python
component_workflow(component='C3', action='run', machine={
    'id': 'run', 'initial': 'start', 'states': {
        'start': {'on': {'start': {'target': 'running', 'guard': {'type': 'matchesTrace',
            'params': {'kind': 'trigger', 'target': 'worker', 'detail': {'transport': 'in_process', 'entry': 'worker.run'}}}}}},
        'running': {'on': {'invoke': {'target': 'returning', 'guard': {'type': 'matchesTrace',
            'params': {'kind': 'effect', 'target': 'C3', 'outcome': 'called'}}}}},
        'returning': {'on': {'return': {'target': 'done', 'guard': {'type': 'matchesTrace',
            'params': {'kind': 'output', 'outcome': 'ready'}}}}},
        'done': {'type': 'final'}}})
```
