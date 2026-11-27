---
atom_family: SPEC
atom_id: AN-S-5041
container:
  component: C71
tier: 0
context:
  template: solution
  lens: DES
relations:
  ANSWERS:
  - AN-S-3333@35-draft
state:
  status: draft
  version: 1
  updated_at: '2026-11-26T23:49:21Z'
---
## Summary

Serve View SQL and Structure

## Claim

### Prose Claim

Keep authored View SQL in its Workspace. Use DuckDB tokens to find a
trailing display directive. Check, Run, and Save validate the SELECT before
it. Recognize the optional layout in Graph and Imports directives.
Save retains the authored SQL and comments.

Project Component Seeds from the accepted Structure in the admission
transaction. Rebuild the projection from retained Structure on an older
bound database that lacks it.

### Formal Claim

```python
component_workflow(component='C71', action='admit_structure_projection', machine={
    'id': 'c71_admit_structure_projection', 'initial': 'idle', 'states': {
        'idle': {'on': {'requested': {'to': 'admitting', 'expect': {
            'kind': 'trigger', 'target': 'admit_structure_projection'}}}},
        'admitting': {'on': {
            'committed': {'to': 'published', 'expect': {'kind': 'effect',
                'target': 'C71.structure_projection', 'outcome': 'committed'}},
            'rejected': {'to': 'done', 'expect': {'kind': 'output', 'outcome': 'failed'}},
        }},
        'published': {'on': {'succeeded': {'to': 'done', 'expect': {
            'kind': 'output', 'outcome': 'succeeded'}}}},
        'done': {'type': 'final'},
    },
})
```

```python
component_workflow(component='C71', action='save_view_sql', machine={
    'id': 'c71_save_view_sql', 'initial': 'idle', 'states': {
        'idle': {'on': {'view_requested': {'to': 'checking', 'expect': {
            'kind': 'trigger', 'target': 'save_view_sql',
            'bind': {'sql': 'authored_sql'}}}}},
        'checking': {'on': {
            'validated': {'to': 'saving', 'expect': {'kind': 'effect',
                'target': 'C71.view_select', 'outcome': 'validated'}},
            'rejected': {'to': 'done', 'expect': {'kind': 'output', 'outcome': 'failed'}},
        }},
        'saving': {'on': {
            'view_saved': {'to': 'returning', 'expect': {
                'kind': 'effect', 'target': 'C71.saved_view', 'outcome': 'saved',
                'same_as': {'authored_sql': 'sql'}}},
            'rejected': {'to': 'done', 'expect': {'kind': 'output', 'outcome': 'failed'}},
        }},
        'returning': {'on': {'succeeded': {'to': 'done', 'expect': {
            'kind': 'output', 'outcome': 'succeeded'}}}},
        'done': {'type': 'final'},
    },
})
```

```python
component_workflow(component='C71', action='check_view_sql', machine={
    'id': 'c71_check_view_sql', 'initial': 'idle', 'states': {
        'idle': {'on': {'requested': {'to': 'checking', 'expect': {
            'kind': 'trigger', 'target': 'check_view_sql'}}}},
        'checking': {'on': {
            'validated': {'to': 'executing', 'expect': {'kind': 'effect',
                'target': 'C71.view_select', 'outcome': 'validated'}},
            'rejected': {'to': 'done', 'expect': {'kind': 'output', 'outcome': 'failed'}},
        }},
        'executing': {'on': {
            'ready': {'to': 'returning', 'expect': {'kind': 'effect',
                'target': 'C71.check_result', 'outcome': 'ready'}},
            'rejected': {'to': 'done', 'expect': {'kind': 'output', 'outcome': 'failed'}},
        }},
        'returning': {'on': {'succeeded': {'to': 'done', 'expect': {
            'kind': 'output', 'outcome': 'succeeded'}}}},
        'done': {'type': 'final'},
    },
})
```

```python
component_workflow(component='C71', action='run_view_sql', machine={
    'id': 'c71_run_view_sql', 'initial': 'idle', 'states': {
        'idle': {'on': {'requested': {'to': 'checking', 'expect': {
            'kind': 'trigger', 'target': 'run_view_sql'}}}},
        'checking': {'on': {
            'validated': {'to': 'executing', 'expect': {'kind': 'effect',
                'target': 'C71.view_select', 'outcome': 'validated'}},
            'rejected': {'to': 'done', 'expect': {'kind': 'output', 'outcome': 'failed'}},
        }},
        'executing': {'on': {
            'ready': {'to': 'returning', 'expect': {'kind': 'effect',
                'target': 'C71.view_result', 'outcome': 'ready'}},
            'rejected': {'to': 'done', 'expect': {'kind': 'output', 'outcome': 'failed'}},
        }},
        'returning': {'on': {'succeeded': {'to': 'done', 'expect': {
            'kind': 'output', 'outcome': 'succeeded'}}}},
        'done': {'type': 'final'},
    },
})
```

```python
component_workflow(component='C71', action='admit_console_graph', machine={
    'id': 'c71_admit_console_graph', 'initial': 'idle', 'states': {
        'idle': {'on': {'requested': {'to': 'checking', 'expect': {'kind': 'trigger'}}}},
        'checking': {'on': {
            'admitted': {'to': 'publishing', 'expect': {
                'kind': 'effect', 'target': 'C71.graph', 'outcome': 'admitted'}},
            'refused': {'to': 'done', 'expect': {'kind': 'output', 'outcome': 'refused'}},
        }},
        'publishing': {'on': {'published': {'to': 'done', 'expect': {'kind': 'output', 'outcome': 'published'}}}},
        'done': {'type': 'final'},
    },
})
```
