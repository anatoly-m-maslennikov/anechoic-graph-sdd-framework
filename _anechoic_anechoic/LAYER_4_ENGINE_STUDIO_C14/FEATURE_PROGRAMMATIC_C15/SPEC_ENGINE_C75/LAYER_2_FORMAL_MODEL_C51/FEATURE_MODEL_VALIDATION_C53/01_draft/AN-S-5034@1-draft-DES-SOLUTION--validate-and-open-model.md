---
atom_family: SPEC
atom_id: AN-S-5034
container:
  component: C53
tier: 0
context:
  template: solution
  lens: DES
relations:
  ANSWERS:
  - AN-S-3067@42-draft
state:
  status: draft
  version: 1
  updated_at: '2026-11-27T00:00:00+00:00'
---

## Summary

Validate a proposed Model instance before its caller writes it.

## Claim

### Prose Claim

Validate fields and Relations, construct the instance, apply named and
inherited population checks, then return the instance or raise an error.

Open the accepted admitted-Model artifact for the caller. Fail if the artifact
is unavailable or invalid and record that failure. The exact input, verification predicates, and
returned representation remain unresolved.

### Formal Claim

```python
component_workflow(component='C53', action='validate_proposed_model_instance',
    machine={'id': 'c53_validate_proposed_model_instance', 'initial': 'idle', 'states': {
        'idle': {'on': {'validation_requested': {'target': 'validating', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'trigger'}}}}},
        'validating': {'on': {'field_or_relation_invalid': {'target': 'rejecting', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'effect', 'target': 'validation', 'outcome': 'rejected'}}}, 'check_or_population_invalid': {'target': 'rejecting', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'effect', 'target': 'validation', 'outcome': 'rejected'}}}, 'model_rules_passed': {'target': 'returning', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'effect', 'target': 'model_rules', 'outcome': 'passed'}}}}},
        'rejecting': {'on': {'validation_error_reported': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'output', 'outcome': 'failed'}}}}},
        'returning': {'on': {'validated_instance_returned': {'target': 'succeeded', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'output', 'outcome': 'succeeded'}}}}},
        'succeeded': {'type': 'final'},
        'failed': {'type': 'final'},
    }})
```

```python
component_workflow(component='C53', action='open_admitted_model',
    machine={'id': 'c53_open_admitted_model', 'initial': 'idle', 'states': {
        'idle': {'on': {'open_requested': {'target': 'opening', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'trigger', 'target': 'admitted_model', 'detail': {'interface': 'admitted_model', 'action': 'open_admitted_model', 'entry': 'FEATURE_MODEL_VALIDATION__shared.open_admitted_model', 'transport': 'in_process'}}}}}},
        'opening': {'on': {'admitted_model_opened': {'target': 'returning', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'effect', 'target': 'C53.admitted_model', 'outcome': 'opened'}}}, 'artifact_unavailable_or_invalid': {'target': 'reporting_failure', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'effect', 'target': 'C53.admitted_model', 'outcome': 'failed'}}}}},
        'reporting_failure': {'on': {'failure_reported': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'output', 'outcome': 'failed'}}}}},
        'returning': {'on': {'open_succeeded': {'target': 'succeeded', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'output', 'outcome': 'succeeded'}}}}},
        'succeeded': {'type': 'final'},
        'failed': {'type': 'final'},
    }})
```

