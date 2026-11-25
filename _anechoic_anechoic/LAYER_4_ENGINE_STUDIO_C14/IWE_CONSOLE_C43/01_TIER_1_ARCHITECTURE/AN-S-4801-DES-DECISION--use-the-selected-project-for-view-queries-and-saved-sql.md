---
atom_family: SPEC
atom_id: AN-S-4801
container:
  component: C43
tier: 1
context:
  template: DECISION
  lens: DES
relations:
  IS_SOLUTION_FOR:
  - AN-S-4794@1
  IS_REFERENCE:
  - AN-S-2550@22
  - AN-S-1943@10
state:
  status: "active"
  version: 3
  updated_at: "2026-11-24T23:05:55.112870+00:00"
---

## Summary

Use the selected Project for View queries and saved SQL

## Claim

### Prose Claim

The browser sends View Run, Check, and saved SQL operations through the
selected Project interface. Run & Save uses View Run with `save: true`.
The Backend validates requests and delegates to the Project Kernel.

Save View stores the View SQL. Loading a saved ID or URL supplies its
exact SQL for a separate Run. The browser shows results, saved identities,
and failures. If saving fails after Run, keep the result and show the save error.

### Formal Claim

```python
component_workflow(
    component='C43',
    action='workbench_run_view',
    machine={
        'id': 'c43_workbench_run_view',
        'initial': 'idle',
        'states': {
            'idle': {'on': {
                'run_selected': {'target': 'running', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'trigger'}}},
            }},
            'running': {'on': {
                'project_run_succeeded': [
                    {'target': 'displaying', 'guard': {'type': 'matchesTrace', 'params':
                        {'kind': 'effect', 'target': 'C45', 'outcome': 'succeeded'}}},
                    {'target': 'displaying', 'guard': {'type': 'matchesTrace', 'params':
                        {'kind': 'effect', 'target': 'C82', 'outcome': 'succeeded'}}},
                ],
                'project_run_failed': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'displaying': {'on': {
                'result_displayed': {'target': 'succeeded', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'succeeded'}}},
                'display_failed': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'succeeded': {'type': 'final'},
            'failed': {'type': 'final'},
        },
    },
)
```

## Details

The Formal Claim covers View Run. C82 serves `beta_next`. C45 serves
`current`. Trace conformance requires recorded evidence.
