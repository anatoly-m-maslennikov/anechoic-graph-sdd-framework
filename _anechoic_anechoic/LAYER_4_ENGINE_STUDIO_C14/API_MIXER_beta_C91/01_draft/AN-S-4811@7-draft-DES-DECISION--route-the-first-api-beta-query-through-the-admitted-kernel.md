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
  status: draft
  version: 7
  updated_at: '2026-11-27T18:27:25.623815+00:00'
relations:
  IS_SOLUTION_FOR:
  - AN-S-4809@6
---

## Summary

Route the first API Beta query through the admitted Kernel

## Claim

### Prose Claim

Use the C91 direct and shared API entry points in AN-S-4809@6. Check the
pinned direct binding against the Project peers before serving queries. In
shared mode, release every acquired lease on every exit, including errors
and stale-binding refusal. C68 owns the lease record. Revalidate after
dispatch and discard the result if the binding changed.

Run C91 through its standalone entry points. Compare catalog capabilities,
results, and errors on the same Project when verifying standalone runs.

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
                'query_run_requested': {'target': 'validating', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'trigger'}}},
            }},
            'validating': {'on': {
                'query_sent_to_kernel': {'target': 'direct_reporting', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'effect', 'target': 'C71'}}},
                'lease_acquired': {'target': 'leased', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'effect', 'target': 'C68'}}},
                'query_refused': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'output'}}},
            }},
            'leased': {'on': {
                'query_sent_to_kernel': {'target': 'leased_reporting', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'effect', 'target': 'C71'}}},
                'query_refusal_pending': {'target': 'release_failure', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'effect', 'target': 'C91'}}},
            }},
            'direct_reporting': {'on': {
                'kernel_result_returned': {'target': 'completed', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'output', 'outcome': 'completed'}}},
                'kernel_failure_returned': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'output', 'outcome': 'failed'}}},
                'stale_binding_refused': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'leased_reporting': {'on': {
                'binding_valid_result_pending': {'target': 'release_success', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'effect', 'target': 'C91'}}},
                'kernel_failure_pending': {'target': 'release_failure', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'effect', 'target': 'C91'}}},
                'stale_binding_detected': {'target': 'release_failure', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'effect', 'target': 'C91'}}},
            }},
            'release_success': {'on': {
                'lease_released': {'target': 'return_success', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'effect', 'target': 'C68'}}},
            }},
            'release_failure': {'on': {
                'lease_released': {'target': 'return_failure', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'effect', 'target': 'C68'}}},
            }},
            'return_success': {'on': {
                'kernel_result_returned': {'target': 'completed', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'output', 'outcome': 'completed'}}},
            }},
            'return_failure': {'on': {
                'query_refused': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'output', 'outcome': 'failed'}}},
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
