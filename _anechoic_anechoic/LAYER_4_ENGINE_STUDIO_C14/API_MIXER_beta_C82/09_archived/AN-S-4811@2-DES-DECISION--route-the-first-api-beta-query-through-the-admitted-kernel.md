---
atom_family: SPEC
atom_id: AN-S-4811
container:
  component: C82
tier: 1
context:
  template: DECISION
  lens: DES
state:
  status: "archived"
  version: 2
  updated_at: '2026-11-24T19:35:54.327066+00:00'
relations:
  IS_SOLUTION_FOR:
  - AN-S-4810@2
  IS_REFERENCE:
  - AN-S-3361@2
  - AN-S-3387@2
---

## Summary

Route the first API Beta query through the admitted Kernel

## Claim

### Prose Claim

C21 starts `python -m API_MIXER_beta_C82.API_MIXER_beta_C82__shared` with
`--role api` and the direct startup arguments. Check the pinned binding
against the Project peers before serving queries.

C21 starts `python -m API_MIXER_beta_C82.shared_runtime` with the API and
peer-owner socket paths. Use C70 `select`, `status`, and `lease` over private
IPC. Release each lease when the request ends. Discard results when
the binding changes during the request.

Use the same Backend selector for baseline and `beta_next`. Compare the
supported query family on the same Project before cutover. Check catalog
capabilities, results, and errors.

### Formal Claim

```python
component_workflow(
    component='C82',
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
