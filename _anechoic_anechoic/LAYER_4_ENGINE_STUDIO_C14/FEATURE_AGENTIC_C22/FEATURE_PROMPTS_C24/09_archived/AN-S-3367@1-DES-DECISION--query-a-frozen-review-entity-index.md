---
atom_family: SPEC
atom_id: AN-S-3367
container:
  component: C24
tier: 1
context:
  template: DECISION
  lens: DES
relations:
  IS_REFERENCE:
  - AN-S-3361@2
  - AN-S-3387@1
  IS_SOLUTION_FOR:
  - AN-S-3309@2
state:
  status: archived
  version: 1
  updated_at: '2026-11-22T23:52:17.262612+00:00'
---

## Summary

Query a frozen review Entity index

## Claim

### Prose Claim

Given a frozen context and nonempty query, return matching Entity records
as ranked JSON candidates, with exact names first.

### Formal Claim

```python
component_workflow(
    component='C24',
    action='query_frozen_review_entity_index',
    machine={
        'id': 'c24_query_frozen_review_entity_index',
        'initial': 'idle',
        'states': {
            'idle': {'on': {
                'query_requested': {'target': 'searching', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'trigger'}}},
            }},
            'searching': {'on': {
                'frozen_context_file_read': {'target': 'responding', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C24', 'outcome': 'succeeded'}}},
            }},
            'responding': {'on': {
                'candidate_records_returned': {'target': 'succeeded', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'succeeded'}}},
            }},
            'succeeded': {'type': 'final'},
        },
    },
)
```

## Details

This Solution defines the expected event sequence for the selected workflow.
Trace conformance requires recorded evidence.
