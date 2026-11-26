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
  - AN-S-3184@3-draft
state:
  status: draft
  version: 3
  updated_at: "2026-11-25T10:58:29.166498+00:00"
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
                'field_or_relation_invalid': {'target': 'rejecting', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'validation', 'outcome': 'rejected'}}},
                'check_or_population_invalid': {'target': 'rejecting', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'validation', 'outcome': 'rejected'}}},
                'model_rules_passed': {'target': 'returning', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'model_rules', 'outcome': 'passed'}}},
            }},
            'rejecting': {'on': {
                'validation_error_reported': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'returning': {'on': {
                'validated_instance_returned': {'target': 'succeeded', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'succeeded'}}},
            }},
            'succeeded': {'type': 'final'},
            'failed': {'type': 'final'},
        },
    },
)
```

```python
component_workflow(
    component='C53',
    action='open_admitted_model',
    machine={
        'id': 'c53_open_admitted_model',
        'initial': 'idle',
        'states': {
            'idle': {'on': {
                'open_requested': {'target': 'opening', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'trigger', 'target': 'admitted_model', 'detail': {
                        'interface': 'admitted_model', 'action': 'open_admitted_model',
                        'entry': 'FEATURE_MODEL_VALIDATION__shared.open_admitted_model',
                        'transport': 'in_process',
                    }}}},
            }},
            'opening': {'on': {
                'admitted_model_opened': {'target': 'returning', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C53.admitted_model', 'outcome': 'opened'}}},
                'artifact_unavailable_or_invalid': {'target': 'reporting_failure', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C53.admitted_model', 'outcome': 'failed'}}},
            }},
            'reporting_failure': {'on': {
                'failure_reported': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'returning': {'on': {
                'open_succeeded': {'target': 'succeeded', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'succeeded'}}},
            }},
            'succeeded': {'type': 'final'},
            'failed': {'type': 'final'},
        },
    },
)
```

## Details

This Solution defines the expected event sequence for the selected workflow.
The `model_rules` effect summarizes successful applicable checks. The
workflow has no instance-write effect. These events are expected evidence;
trace conformance requires them to be recorded.

The `validation` rejection effect records a failed rule.
