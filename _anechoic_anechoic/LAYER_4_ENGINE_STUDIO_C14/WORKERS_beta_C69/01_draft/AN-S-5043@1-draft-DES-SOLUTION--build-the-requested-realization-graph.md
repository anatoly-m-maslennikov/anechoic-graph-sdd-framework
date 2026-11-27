---
atom_family: SPEC
atom_id: AN-S-5043
container:
  component: C69
tier: 0
context:
  template: solution
  lens: DES
relations:
  ANSWERS:
  - AN-S-3334@36-draft
state:
  status: draft
  version: 1
  updated_at: "2026-11-27T00:12:14Z"
---
## Summary

Build the requested Realization Graph

## Claim

### Prose Claim

Run C61 with the accepted Structure and direct capture to the Graph
artifact. The Orchestrator sends the witness to C71 for admission.

### Formal Claim

```python
component_workflow(component='C69', action='build_console_graph', machine={
    'id': 'c69_build_console_graph', 'initial': 'idle', 'states': {
        'idle': {'on': {'requested': {'to': 'checking', 'expect': {'kind': 'trigger'}}}},
        'checking': {'on': {
            'captured': {'to': 'built', 'expect': {
                'kind': 'effect', 'target': 'C69.graph', 'outcome': 'built'}},
            'refused': {'to': 'done', 'expect': {'kind': 'output', 'outcome': 'refused'}},
        }},
        'built': {'on': {'completed': {'to': 'done', 'expect': {'kind': 'output', 'outcome': 'built'}}}},
        'done': {'type': 'final'},
    },
})
```
