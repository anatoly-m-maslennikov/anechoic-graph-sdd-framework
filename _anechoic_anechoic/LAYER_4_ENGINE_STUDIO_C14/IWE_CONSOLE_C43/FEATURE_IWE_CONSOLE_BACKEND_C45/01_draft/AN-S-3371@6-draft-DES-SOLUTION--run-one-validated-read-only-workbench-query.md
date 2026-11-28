---
atom_family: SPEC
atom_id: AN-S-3371
container:
  component: C45
tier: 0
context:
  template: solution
  lens: DES
relations:
  ANSWERS:
  - AN-S-3059@66-draft
state:
  status: draft
  version: 6
  updated_at: "2026-11-28T10:18:04Z"
---

## Summary

Run one validated read-only IWE Console query

## Claim

### Prose Claim

Delegate to the Kernel bound to the selected Project. The modeled success
path delegates to C59 and returns a result. The modeled refusal path rejects
an invalid request envelope before provider dispatch. Other paths, including
SQL rejection after dispatch and Tool failures, are outside this trace model.

### Formal Claim

```python
component_workflow(
    component='C45', action='workbench_backend_run_query',
    machine={
        'id': 'c45_workbench_backend_run_query', 'initial': 'idle',
        'states': {
            'idle': {'on': {
                'request': {'to': 'validating', 'expect': {'kind': 'trigger'}},
            }},
            'validating': {'on': {
                'delegate': {'to': 'executing', 'expect': {
                    'kind': 'effect', 'target': 'C59', 'outcome': 'succeeded'}},
                'refuse': {'to': 'done', 'expect': {
                    'kind': 'output', 'outcome': 'refused'}},
            }},
            'executing': {'on': {
                'return': {'to': 'done', 'expect': {
                    'kind': 'output', 'outcome': 'succeeded'}},
            }},
            'done': {'type': 'final'},
        },
    },
)
```

## Details

Use AN-S-2686 for trace evidence. C59 receives requests at `POST /database`.
The current Tool API uses `POST /`; the legacy Workbench API uses
`POST /workbench`.
