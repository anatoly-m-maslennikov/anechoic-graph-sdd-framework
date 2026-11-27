---
atom_family: SPEC
atom_id: AN-S-5044
container:
  component: C21
tier: 0
context:
  template: solution
  lens: DES
relations:
  ANSWERS:
  - AN-S-3044@68-draft
state:
  status: draft
  version: 1
  updated_at: "2026-11-27T05:57:13.189Z"
---
## Summary

Forward a Console Document

## Claim

### Prose Claim

Admit the Project binding and check the route's Project name. Send the
Atom selector unchanged to the bound C91 API through `shared_api` in
shared mode or `project_api` in direct mode. Return the API response.

### Formal Claim

```python
component_workflow(component='C21', action='forward_console_document', machine={
    'id': 'c21_forward_console_document', 'initial': 'idle',
    'states': {
        'idle': {'on': {'requested': {'to': 'selecting', 'expect': {
            'kind': 'trigger', 'target': 'workbench_http',
            'detail': {'transport': 'http',
                       'endpoint': 'POST /anechoic/{project_name}/api/interface',
                       'route_name': 'interface', 'tool': 'iwe_console_atom_document'}}}}},
        'selecting': {'on': {
            'current': {'to': 'current_reply', 'expect': {
                'kind': 'effect', 'target': 'C21.project_binding', 'outcome': 'admitted',
                'detail': {'project_name': 'Example', 'ref_id': 'EX-T-1'}}},
            'exact': {'to': 'exact_reply', 'expect': {
                'kind': 'effect', 'target': 'C21.project_binding', 'outcome': 'admitted',
                'detail': {'project_name': 'Example', 'ref_id': 'EX-T-1@1'}}},
            'wrong_project': {'to': 'refusal', 'expect': {
                'kind': 'effect', 'target': 'C21.project_binding', 'outcome': 'refused',
                'detail': {'project_name': 'Other', 'ref_id': 'EX-T-1'}}},
        }},
        'current_reply': {'on': {'observed': {'to': 'current_end', 'expect': {
            'kind': 'effect', 'target': 'C21.console_document', 'outcome': 'returned',
            'detail': {'status': 200, 'exact_ref': 'EX-T-1@2'}}}}},
        'exact_reply': {'on': {'observed': {'to': 'exact_end', 'expect': {
            'kind': 'effect', 'target': 'C21.console_document', 'outcome': 'returned',
            'detail': {'status': 200, 'exact_ref': 'EX-T-1@1'}}}}},
        'refusal': {'on': {'observed': {'to': 'refusal_end', 'expect': {
            'kind': 'effect', 'target': 'C21.console_document', 'outcome': 'refused',
            'detail': {'status': 404}}}}},
        'current_end': {'on': {'finished': {'to': 'done', 'expect': {
            'kind': 'output', 'outcome': 'current'}}}},
        'exact_end': {'on': {'finished': {'to': 'done', 'expect': {
            'kind': 'output', 'outcome': 'exact'}}}},
        'refusal_end': {'on': {'finished': {'to': 'done', 'expect': {
            'kind': 'output', 'outcome': 'wrong_project'}}}},
        'done': {'type': 'final'},
    },
})
```
