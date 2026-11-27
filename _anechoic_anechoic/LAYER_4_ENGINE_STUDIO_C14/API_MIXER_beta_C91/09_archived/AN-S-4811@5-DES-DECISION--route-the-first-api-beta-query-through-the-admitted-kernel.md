---
atom_family: SPEC
atom_id: AN-S-4811
container:
  component: C91
tier: 1
context:
  template: DECISION
  lens: DES
state:
  status: archived
  version: 5
  updated_at: "2026-11-27T17:35:01.150345+00:00"
relations:
  IS_SOLUTION_FOR:
  - AN-S-4810@3

---

## Summary

Route the first API Beta query through the admitted Kernel

## Claim

### Prose Claim

Use the C91 direct and shared API entry points in AN-S-4809. Check the pinned direct binding against the Project peers before serving queries. In shared mode release each lease when the request ends. Discard results when the binding changes during the request.

Select C91 with `beta_next`. Before cutover, compare catalog capabilities,
results, and errors on the same Project against the immutable Beta baseline.

### Formal Claim

```python
component_workflow(
    component='C91',
    action='run_api_beta_query',
    machine={
        'id': 'c82_run_api_beta_query',
        'initial': 'idle',
        'states': {
            'idle': {'on': {
                'query_run_requested': {'target': 'validating', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'trigger'}}},
            }},
            'validating': {'on': {
                'query_sent_to_kernel': {'target': 'reporting', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C71'}}},
                'query_refused': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output'}}},
            }},
            'reporting': {'on': {
                'kernel_result_returned': {'target': 'completed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'completed'}}},
                'kernel_failure_returned': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'completed': {'type': 'final'},
            'failed': {'type': 'final'},
        },
    },
)
```

## Details

The Formal Claim describes the expected sequence for `query_run`.
Trace conformance requires recorded evidence.
