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
  - AN-S-5018@1-draft
state:
  status: draft
  version: 1
  updated_at: '2026-11-26T21:01:26.237634+00:00'
---

## Summary

Compile a Project Structure snapshot

## Claim

### Prose Claim

Read the selected Project Manifest and the active Component and Seed Manifests. Validate their declarations and containment against the supplied admitted Model.

Check the carrier inventory and source pins again before returning the snapshot. Return the Model fingerprint and the Project Manifest digest with the Component and Seed records.

### Formal Claim

```python
component_workflow(
    component='C93', action='compile_project_structure',
    machine={'id': 'c93_compile_project_structure', 'initial': 'idle', 'states': {
        'idle': {'on': {
            'requested': {'to': 'validate', 'expect': {
                'kind': 'trigger', 'target': 'compile_project_structure',
                'detail': {'transport': 'in_process', 'entry': 'LAYER_2_PROJECT_STRUCTURE_C93__shared.compile_structure'},
                'bind': {'model': 'model_sha256', 'manifest': 'manifest_sha256'}}},
        }},
        'validate': {'on': {
            'snapshot_ready': {'to': 'return', 'expect': {
                'kind': 'effect', 'target': 'C93.structure_snapshot', 'outcome': 'ready',
                'same_as': {'model_sha256': 'model', 'manifest_sha256': 'manifest'}}},
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
