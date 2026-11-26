---
atom_family: SPEC
atom_id: AN-S-4791
container:
  component: C22
tier: 1
context:
  template: decision
  lens: DES
relations:
  IS_SOLUTION_FOR:
  - AN-S-4790@2-draft
state:
  status: draft
  version: 2
  updated_at: '2026-11-25T11:02:11.485674+00:00'
---

## Summary

Supply agent guidance

## Claim

### Prose Claim

C23 and C24 hold skill and prompt guidance. In this conceptual consumer flow, an agent seeks guidance, the guidance is available, and the agent receives it. The guidance does not itself execute an operation.

The sequence is a model of a handoff, not a runtime protocol or proof that an agent used the guidance. It does not prescribe selection or later agent actions.

### Formal Claim

```python
component_workflow(
    component='C22',
    action='consume_agent_guidance',
    machine={
        'id': 'c22_consume_agent_guidance', 'initial': 'idle',
        'states': {
            'idle': {'on': {'guidance_sought': {'target': 'selecting', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'trigger', 'target': 'guidance'}}}}},
            'selecting': {'on': {'guidance_available': {'target': 'handoff', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'effect', 'target': 'guidance', 'outcome': 'available'}}}}},
            'handoff': {'on': {'guidance_received': {'target': 'done', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'output', 'outcome': 'guidance_received'}}}}},
            'done': {'type': 'final'},
        },
    },
)
```

## Details

The flow covers a successful conceptual handoff only. No operation execution event is admitted by this flow; the Contract forbids that effect during the handoff. Other conditions and later agent behavior are outside this model.
