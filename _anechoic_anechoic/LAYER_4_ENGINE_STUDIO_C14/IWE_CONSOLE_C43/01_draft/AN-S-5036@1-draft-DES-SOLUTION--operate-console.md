---
atom_family: SPEC
atom_id: AN-S-5036
container:
  component: C43
tier: 0
context:
  template: solution
  lens: DES
relations:
  ANSWERS:
  - AN-S-3046@7-draft
state:
  status: draft
  version: 1
  updated_at: "2026-11-26T23:31:05Z"
---
## Summary

Operate the selected Project in IWE Console

## Claim

### Prose Claim

Delegate View and document interaction to C46. Read the Project binding
from the Workspace and use it to dispatch queries, lifecycle operations,
and rebuilds through C21. Bind the admitted Project identity, which
distinguishes Projects that have the same name. Show completion only
when the successful API receipt identifies the same Project. Report
refusal, failure, or a mismatched receipt through the failed outcome.

### Formal Claim

```python
component_workflow(component='C43', action='operate_console', machine={
    'id': 'c43_operate_console', 'initial': 'idle', 'states': {
        'idle': {'on': {'requested': {'to': 'running', 'expect': {
            'kind': 'trigger', 'bind': {'project': 'project'}}}}},
        'running': {'on': {
            'dispatched': {'to': 'awaiting_receipt', 'expect': {
                'kind': 'effect', 'target': 'C21.workbench_http', 'outcome': 'dispatched',
                'same_as': {'project': 'project'}}},
            'failed': {'to': 'done', 'expect': {'kind': 'output', 'outcome': 'failed'}},
        }},
        'awaiting_receipt': {'on': {
            'received': {'to': 'rendering', 'expect': {
                'kind': 'effect', 'target': 'C21.workbench_http', 'outcome': 'succeeded',
                'same_as': {'project': 'project'}}},
            'failed': {'to': 'done', 'expect': {'kind': 'output', 'outcome': 'failed'}},
        }},
        'rendering': {'on': {
            'render_view': {'to': 'rendered', 'expect': {
                'kind': 'effect', 'target': 'C46.console', 'outcome': 'view_displayed',
                'detail': {'component': 'C46', 'manifest': 'AN-S-3060@12-draft',
                           'action': 'render_console_view', 'output': 'succeeded',
                           'interface': 'console_view', 'transport': 'in_process'},
                'same_as': {'project': 'project'},
            }},
        }},
        'rendered': {'on': {'completed': {'to': 'returning', 'expect': {
            'kind': 'effect', 'outcome': 'console_operation_completed', 'target': 'C43.console',
            'same_as': {'project': 'project'}}}}},
        'returning': {'on': {'succeeded': {'to': 'done', 'expect': {'kind': 'output', 'outcome': 'succeeded'}}}},
        'done': {'type': 'final'},
    },
})
```
