---
atom_family: SPEC
atom_id: AN-S-5076
container:
  component: C21
tier: 0
context:
  template: solution
  lens: DES
relations:
  ANSWERS:
  - AN-S-3044@69-draft
state:
  status: draft
  version: 1
  updated_at: '2026-11-27T17:00:30.949693+00:00'
---
## Summary

Package shared beta Tool OpenAPI in the runtime image

## Claim

### Prose Claim

Run the C91 exporter in the beta_next build stage after copying its code. Write its output into the image. Test the emitted Version against the same image's version.toml.

### Formal Claim

```python
component_workflow(
    component='C21',
    action='build_beta_next_tool_openapi',
    machine={
        'id': 'c21_pack_tool_openapi',
        'initial': 'idle',
        'states': {
            'idle': {'on': {
                'requested': {'to': 'read_version', 'expect': {'kind': 'trigger'}},
            }},
            'read_version': {'on': {
                'read': {'to': 'build', 'expect': {
                    'kind': 'effect', 'target': 'framework_version',
                    'outcome': 'read', 'bind': {'framework': 'version'},
                }},
                'failure': {'to': 'done', 'expect': {
                    'kind': 'output', 'outcome': 'failed',
                }},
            }},
            'build': {'on': {
                'written': {'to': 'report', 'expect': {
                    'kind': 'effect', 'target': 'tool_openapi',
                    'outcome': 'written', 'same_as': {'version': 'framework'},
                    'detail': {
                        'path': '/usr/local/share/anechoic/openapi.json',
                        'openapi': '3.1.0',
                    },
                }},
                'failure': {'to': 'done', 'expect': {
                    'kind': 'output', 'outcome': 'failed',
                }},
            }},
            'report': {'on': {
                'success': {'to': 'done', 'expect': {
                    'kind': 'output', 'outcome': 'packaged',
                }},
            }},
            'done': {'type': 'final'},
        },
    },
)
```
