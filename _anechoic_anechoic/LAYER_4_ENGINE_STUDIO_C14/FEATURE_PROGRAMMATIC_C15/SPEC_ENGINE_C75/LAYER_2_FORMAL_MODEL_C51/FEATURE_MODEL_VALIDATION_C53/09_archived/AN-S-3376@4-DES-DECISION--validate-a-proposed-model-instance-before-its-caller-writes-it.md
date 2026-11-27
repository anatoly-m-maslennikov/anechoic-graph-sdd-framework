---
atom_family: SPEC
atom_id: AN-S-3376
container:
  component: C53
tier: 1
context:
  template: DECISION
  lens: DES
relations:
  IS_SOLUTION_FOR:
  - AN-S-3184@2
state:
  status: archived
  version: 4
  updated_at: "2026-11-27T16:16:01.404965+00:00"
---

## Summary

Validate a proposed Model instance before its caller writes it.

## Claim

### Prose Claim

Validate fields and Relations, construct the instance, apply named and
inherited population checks, then return the instance or raise an error.

### Formal Claim

```python
component_workflow(
    component='C53',
    action='validate_proposed_model_instance',
    machine={
        'id': 'c53_validate_proposed_model_instance',
        'initial': 'idle',
        'states': {
            'idle': {'on': {
                'validation_requested': {'target': 'validating', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'trigger'}}},
            }},
            'validating': {'on': {
                'validated_instance_returned': {'target': 'succeeded', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'succeeded'}}},
                'field_or_relation_invalid': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
                'check_or_population_invalid': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'succeeded': {'type': 'final'},
            'failed': {'type': 'final'},
        },
    },
)
```

## Details

Use AN-S-2686 for trace evidence.
