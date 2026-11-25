---
atom_family: SPEC
atom_id: AN-S-3386
container:
  component: C71
tier: 1
context:
  template: DECISION
  lens: DES
relations:
  IS_SOLUTION_FOR:
  - AN-S-3335@30
state:
  status: active
  version: 4
  updated_at: '2026-11-23T23:25:17+00:00'
---
## Summary

Serve a SQL request for the admitted Beta Project generation.

## Claim

### Prose Claim

For a successful new read-only SQL Run, the Database Server checks the
Project binding and accepted generation, then executes and retains the result
before returning it. A query can also append to history.

### Formal Claim

```python
component_workflow(
    component='C71',
    action='beta_database_query',
    machine={
        'id': 'c71_beta_database_query',
        'initial': 'idle',
        'states': {
            'idle': {'on': {
                'database_request_received': {'target': 'step_1', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'trigger'}}},
            }},
            'step_1': {'on': {
                'admitted_generation_read': {'target': 'step_2', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C71'}}},
            }},
            'step_2': {'on': {
                'query_executed_and_retained': {'target': 'responding', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C71'}}},
            }},
            'responding': {'on': {
                'query_result_returned': {'target': 'succeeded', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'succeeded'}}},
            }},
            'succeeded': {'type': 'final'},
        },
    },
)
```

## Details

This Solution models a successful new SQL Run independently of checkpoint,
Archive, incremental admission, and delta behavior. Paging and failure
outcomes are outside this model. Trace conformance requires recorded evidence.
