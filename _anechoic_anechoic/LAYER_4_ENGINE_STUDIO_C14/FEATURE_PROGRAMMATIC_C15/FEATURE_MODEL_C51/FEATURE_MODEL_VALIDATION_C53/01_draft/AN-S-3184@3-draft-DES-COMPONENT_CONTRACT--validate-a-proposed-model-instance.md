---
atom_family: SPEC
atom_id: AN-S-3184
container:
  component: C53
tier: 0
context:
  template: component_contract
  lens: DES
relations:
  ANSWERS:
  - AN-S-3067
state:
  status: draft
  version: 3
  updated_at: "2026-11-25T10:58:29.166498+00:00"
---

## Summary

Validate a proposed Model instance

## Guarantee

Given a proposed instance and the applicable Model Declarations, validate the
supplied Properties and outgoing Relations against their declared types, allowed
values, cardinalities, and endpoint constraints where applicable. Apply named
instance checks and declared uniqueness rules, including inherited uniqueness
rules, against the supplied peer populations.

Return the constructed Model instance if validation succeeds. Report a
validation error if a rule fails. The caller is responsible for writing the
validated instance.


## Claim

### Prose Claim

A returned instance requires the applicable Model rules to pass. The
validator does not write the instance; the caller owns that step.

Open an accepted admitted-Model artifact for an in-process caller. Report
failure if the accepted artifact is unavailable or invalid. The exact input,
verification predicates, and returned representation remain unresolved.

### Formal Claim

```python trace
declare_trace_contract(
    action='validate_proposed_model_instance',
    output='succeeded',
    must_effect=(('model_rules', 'passed'),),
    forbid_effect=('instance_write',),
)
```

```python trace
declare_trace_contract(
    action='validate_proposed_model_instance',
    output='failed',
    must_effect=(('validation', 'rejected'),),
    forbid_effect=('instance_write',),
)
```

```python trace
declare_trace_contract(
    action='open_admitted_model',
    interface='admitted_model',
    transport='in_process',
    entry='FEATURE_MODEL_VALIDATION__shared.open_admitted_model',
    output='succeeded',
    must_effect=(('C53.admitted_model', 'opened'),),
)
```
