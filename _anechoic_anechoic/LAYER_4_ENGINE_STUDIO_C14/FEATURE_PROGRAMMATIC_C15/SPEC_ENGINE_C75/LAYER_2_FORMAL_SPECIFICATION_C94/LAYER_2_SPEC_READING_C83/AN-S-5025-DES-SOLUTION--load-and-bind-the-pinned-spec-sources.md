---
atom_family: SPEC
atom_id: AN-S-5025
concern:
  subject: "Specification"
  path: "Model/Graph/Node//Artifact//SSOT//Prescribed/Content/Atom"
  relation: "is_narrower_than"
container:
  component: C83
tier: 0
context:
  template: solution
  lens: DES
relations:
  ANSWERS:
  - AN-S-4930@2
state:
  status: active
  version: 4
  updated_at: "2026-11-27T16:29:34.309627+00:00"
---

## Summary

Load and bind the pinned Spec sources.

## Approach

Pass through the C95 source record for each bound role. Apply AN-S-4930
for pin and role checks.

## Claim

### Formal Claim

```python
component_workflow(
    component='C83',
    action='load_boundary_model',
    machine={
        'id': 'c83_load_boundary_model',
        'initial': 'idle',
        'states': {
            'idle': {'on': {
                'requested': {'target': 'working', 'guard': {'type': 'matchesTrace',
                    'params': {'kind': 'trigger'}}},
            }},
            'working': {'on': {
                'effect_recorded': {'target': 'returning', 'guard': {'type': 'matchesTrace',
                    'params': {'kind': 'effect', 'target': 'C83.pinned_sources',
                               'outcome': 'loaded',
                               'bind': {'read_pins': 'source_pins'}}}},
            }},
            'returning': {'on': {
                'result_returned': {'target': 'done', 'guard': {'type': 'matchesTrace',
                    'params': {'kind': 'output', 'outcome': 'loaded',
                               'same_as': {'source_pins': 'read_pins'}}}},
            }},
            'done': {'type': 'final'},
        },
    },
)
```
