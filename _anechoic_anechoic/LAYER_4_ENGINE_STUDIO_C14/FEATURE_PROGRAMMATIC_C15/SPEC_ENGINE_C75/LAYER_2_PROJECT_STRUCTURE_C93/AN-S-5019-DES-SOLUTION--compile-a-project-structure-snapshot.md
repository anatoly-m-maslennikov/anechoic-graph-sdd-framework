---
atom_family: SPEC
atom_id: AN-S-5019
container:
  component: C93
tier: 0
context:
  template: solution
  lens: DES
relations:
  ANSWERS:
  - AN-S-5018@6
state:
  status: active
  version: 4
  updated_at: '2026-11-27T07:54:51.074442+00:00'
---
## Summary

Compile a Project Structure snapshot

## Claim

### Prose Claim

Validate containment and the Project Manifest pin against the supplied
Model. Managed compilation consumes staged rows. Offline compilation
reads the selected Project carriers. Return their declared source pins and Component and Seed purposes.

### Formal Claim

```python
component_workflow(
    component='C93', action='compile_project_structure',
    machine={'id': 'c93_compile_project_structure', 'initial': 'idle', 'states': {
        'idle': {'on': {
            'requested': {'to': 'reading', 'expect': {
                'kind': 'trigger', 'target': 'compile_project_structure',
                'detail': {'transport': 'in_process', 'entry': 'LAYER_2_PROJECT_STRUCTURE_C93__shared.compile_structure'},
                'bind': {'model': 'model_sha256', 'manifest': 'manifest_sha256'}}},
        }},
        'reading': {'on': {
            'source': {'to': 'validate', 'expect': {
                'kind': 'effect', 'target': 'C93.source_purposes', 'outcome': 'read',
                'bind': {'component_purpose': 'component_purpose', 'seed_purpose': 'seed_purpose'}}},
            'rejected': {'to': 'done', 'expect': {'kind': 'output', 'outcome': 'failed'}},
        }},
        'validate': {'on': {
            'snapshot': {'to': 'return', 'expect': {
                'kind': 'effect', 'target': 'C93.structure_snapshot', 'outcome': 'ready',
                'same_as': {'model_sha256': 'model', 'manifest_sha256': 'manifest',
                            'component_purpose': 'component_purpose', 'seed_purpose': 'seed_purpose'}}},
            'rejected': {'to': 'done', 'expect': {'kind': 'output', 'outcome': 'failed'}},
        }},
        'return': {'on': {
            'snapshot_returned': {'to': 'done', 'expect': {
                'kind': 'output', 'outcome': 'succeeded',
                'same_as': {'model_sha256': 'model', 'manifest_sha256': 'manifest'}}},
        }},
        'done': {'type': 'final'},
    }},
)
```

```python
component_workflow(component='C93', action='compile_pinned_structure', machine={
    'id': 'c93_compile_pinned_structure', 'initial': 'idle', 'states': {
        'idle': {'on': {'requested': {'to': 'validate', 'expect': {
            'kind': 'trigger', 'target': 'compile_pinned_structure',
            'detail': {'transport': 'in_process', 'entry': 'LAYER_2_PROJECT_STRUCTURE_C93__rows.compile_structure_rows'},
            'bind': {'model': 'model_sha256', 'manifest': 'manifest_sha256',
                     'pins': 'carrier_pins'}}}}},
        'validate': {'on': {
            'compiled': {'to': 'return', 'expect': {'kind': 'effect', 'target': 'C93.structure_snapshot', 'outcome': 'ready',
                'same_as': {'model_sha256': 'model', 'manifest_sha256': 'manifest', 'carrier_pins': 'pins'}}},
            'rejected': {'to': 'done', 'expect': {'kind': 'output', 'outcome': 'failed'}},
        }},
        'return': {'on': {'returned': {'to': 'done', 'expect': {'kind': 'output', 'outcome': 'succeeded',
            'same_as': {'model_sha256': 'model', 'manifest_sha256': 'manifest', 'carrier_pins': 'pins'}}}}},
        'done': {'type': 'final'},
    },
})
```
