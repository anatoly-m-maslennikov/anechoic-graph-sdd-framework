---
atom_family: SPEC
atom_id: AN-S-5023
container:
  component: C95
tier: 0
context:
  template: solution
  lens: DES
relations:
  ANSWERS:
  - AN-S-5021@3
state:
  status: active
  version: 2
  updated_at: '2026-11-27T11:37:27.939414+00:00'
---
## Summary

Read pinned Spec rows from DuckDB

## Claim

### Prose Claim

Accept the snapshot returned by its database owner for the selected Project.
Match each pin against the stored row before returning its Header, body,
exact ref, and carrier digest. Keep the original digest from ingestion.
Check the exact setting of path, Atom identity, revision status, and
container Component against the pin. An optional requested SHA-256
must match. Include the observed digest in the returned source record.
Use an explicit error for missing or mismatched rows and an unavailable
outcome when no snapshot is ready.

### Formal Claim

```python
component_workflow(
    component='C95', action='read_spec_snapshot',
    machine={'id': 'read_spec_snapshot', 'initial': 'check', 'states': {
        'check': {'on': {
            'available': {'to': 'return', 'expect': {
                'kind': 'effect', 'target': 'C95.source_snapshot', 'outcome': 'ready'}},
            'unavailable': {'to': 'done', 'expect': {'kind': 'output', 'outcome': 'unavailable'}},
            'failed': {'to': 'done', 'expect': {'kind': 'output', 'outcome': 'failed'}},
        }},
        'return': {'on': {'ready': {'to': 'done', 'expect': {'kind': 'output', 'outcome': 'ready'}}}},
        'done': {'type': 'final'},
    }},
)
```
