---
atom_family: SPEC
atom_id: AN-S-5034
concern:
  subject: "Model"
  path: "ANECHOIC"
  relation: "is_contained_by"
container:
  component: C53
tier: 0
context:
  template: solution
  lens: DES
relations:
  ANSWERS:
  - AN-S-3067@44
state:
  status: active
  version: 4
  updated_at: "2026-11-27T16:16:01.404965+00:00"
---

## Summary

Validate a proposed Model instance before its caller writes it.

## Claim

### Prose Claim

Validate the supplied model class, properties, outgoing Relations, Relation
Declarations, Model types, checks, population Declarations and peers, and
optional endpoint registry. Construct and return the instance after all checks
pass. Raise an error when validation fails. The caller writes the instance.

Open a generation from its path, Model fingerprint, and descriptor SHA-256.
Verify the descriptor and module bytes, then bind and yield a BoundNativeModel
in a context manager. Binding or verification errors propagate to the caller.
The temporary loaded modules are removed when the context exits. Preserve the
supplied Model fingerprint and descriptor SHA-256 through the opening. The
yielded BoundNativeModel carries that fingerprint, and the verified
descriptor bytes have the supplied digest.

### Formal Claim

```python
component_workflow(component='C53', action='validate_proposed_model_instance',
    machine={'id': 'c53_validate_proposed_model_instance', 'initial': 'idle', 'states': {
        'idle': {'on': {'validation_requested': {'target': 'validating', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'trigger', 'target': 'proposed_model_instance', 'detail': {'interface': 'proposed_model_instance', 'action': 'validate_proposed_model_instance', 'entry': 'FEATURE_MODEL_VALIDATION__shared.validate_model_instance', 'transport': 'in_process'}}}}}},
        'validating': {'on': {'validation_invalid': {'target': 'rejecting', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'effect', 'target': 'validation', 'outcome': 'rejected'}}}, 'model_rules_passed': {'target': 'returning', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'effect', 'target': 'model_rules', 'outcome': 'passed'}}}}},
        'rejecting': {'on': {'validation_error_reported': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'output', 'outcome': 'failed'}}}}},
        'returning': {'on': {'validated_instance_returned': {'target': 'succeeded', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'output', 'outcome': 'succeeded'}}}}},
        'succeeded': {'type': 'final'},
        'failed': {'type': 'final'},
    }})
```

```python
component_workflow(component='C53', action='open_admitted_model',
    machine={'id': 'c53_open_admitted_model', 'initial': 'idle', 'states': {
        'idle': {'on': {'open_requested': {'target': 'opening', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'trigger', 'target': 'admitted_model', 'detail': {'interface': 'admitted_model', 'action': 'open_admitted_model', 'entry': 'FEATURE_MODEL_VALIDATION__shared.open_admitted_model', 'transport': 'in_process'}, 'bind': {'selected_model': 'model_sha256', 'selected_descriptor': 'descriptor_sha256'}}}}}},
        'opening': {'on': {'admitted_model_opened': {'target': 'returning', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'effect', 'target': 'C53.admitted_model', 'outcome': 'opened', 'same_as': {'model_sha256': 'selected_model', 'descriptor_sha256': 'selected_descriptor'}}}}, 'artifact_unavailable_or_invalid': {'target': 'reporting_failure', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'effect', 'target': 'C53.admitted_model', 'outcome': 'failed'}}}}},
        'reporting_failure': {'on': {'failure_reported': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'output', 'outcome': 'failed'}}}}},
        'returning': {'on': {'open_succeeded': {'target': 'succeeded', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'output', 'outcome': 'succeeded', 'same_as': {'model_sha256': 'selected_model', 'descriptor_sha256': 'selected_descriptor'}}}}}},
        'succeeded': {'type': 'final'},
        'failed': {'type': 'final'},
    }})
```

