---
atom_family: SPEC
atom_id: AN-S-4882
container:
  component: C17
tier: 0
context:
  template: component_contract
  lens: DES
relations:
  ANSWERS:
  - AN-S-3053
state:
  status: draft
  version: 1
  updated_at: '2026-11-25T00:00:00+00:00'
---

## Summary

Execute one connector operation.

## Guarantee

A connector declares its supported subset of query, read, create and modify and the admitted payload schema. Reject unsupported operations and invalid requests without effects or hidden Workflow composition.

The logical request has `operation`, `target`, `query`, `delta`, `expected_state`, `authorization` and `context`. Exactly one logical target or query applies. Query and read have no delta; create and modify carry explicit admitted content or edits. Bind existing source-view, schema, permission and precondition authority.

Read returns actual exact Version where applicable and source-state evidence. An explicit pinned or historical expectation must match. Modify requires expected current state; create requires expected absence. Reject missing, ambiguous, stale or unauthorized bindings without substituting a target or view.

Query and read are mutation-free. Create and modify perform only the admitted storage delta after currentness, permission, schema and preview checks. Domain identity, Version, lifecycle, replacement, reference and Workflow decisions remain outside the connector.

Return `data`, `current_state`, `effects` and structured `errors` from observed evidence. Preserve known partial effects; report unknown effects with `effect_uncertain`. Errors do not indicate success. An empty error list requires independent result verification. A no-op requires verification that the requested state is already satisfied and unchanged.

The direct read-only Subject lookup exception in AN-S-2471 uses its closed criteria and canonical provider rather than the seven-member request. It returns the same result roles without mutation. Applicable Workflow recording remains with the caller.

## Claim

### Formal Claim

```python trace
declare_trace_contract(
    action='execute_connector_operation',
    output='read_reported',
    must_effect=(
        ('C17.operation_result', 'verified'),
        ('C17.request', 'admitted'),
        ('C17.backend_dispatch', 'read'),
    ),
    forbid_effect=('C17.admitted_delta', 'C17.workflow_dispatch', 'semantic_target_substitution'),
    must_precede=(
        (('C17.request', 'admitted'), ('C17.backend_dispatch', 'read')),
        (('C17.backend_dispatch', 'read'), ('C17.operation_result', 'verified')),
    ),
)
```

```python trace
declare_trace_contract(
    action='execute_connector_operation',
    output='write_reported',
    must_effect=(
        ('C17.admitted_delta', 'applied'),
        ('C17.operation_result', 'verified'),
        ('C17.request', 'admitted'),
        ('C17.backend_dispatch', 'write'),
    ),
    forbid_effect=('C17.workflow_dispatch', 'semantic_target_substitution'),
    must_precede=(
        (('C17.request', 'admitted'), ('C17.backend_dispatch', 'write')),
        (('C17.backend_dispatch', 'write'), ('C17.admitted_delta', 'applied')),
        (('C17.admitted_delta', 'applied'), ('C17.operation_result', 'verified')),
    ),
)
```

```python trace
declare_trace_contract(
    action='execute_connector_operation',
    output='write_no_op',
    must_effect=(
        ('C17.storage_state', 'verified_unchanged'),
        ('C17.operation_result', 'verified'),
        ('C17.request', 'admitted'),
    ),
    forbid_effect=('C17.admitted_delta', 'C17.workflow_dispatch', 'semantic_target_substitution'),
    must_precede=(
        (('C17.request', 'admitted'), ('C17.storage_state', 'verified_unchanged')),
        (('C17.storage_state', 'verified_unchanged'), ('C17.operation_result', 'verified')),
    ),
)
```

```python trace
declare_trace_contract(
    action='execute_connector_operation',
    output='write_uncertain',
    must_effect=(
        ('C17.effect_uncertain', 'reported'),
        ('C17.request', 'admitted'),
        ('C17.backend_dispatch', 'write'),
    ),
    forbid_effect=('C17.operation_result', 'C17.workflow_dispatch', 'semantic_target_substitution'),
    must_precede=(
        (('C17.request', 'admitted'), ('C17.backend_dispatch', 'write')),
        (('C17.backend_dispatch', 'write'), ('C17.effect_uncertain', 'reported')),
    ),
)
```

```python trace
declare_trace_contract(
    action='execute_connector_operation',
    output='write_partial_failure',
    must_effect=(
        ('C17.request', 'admitted'),
        ('C17.backend_dispatch', 'write'),
        ('C17.partial_effects', 'reported'),
        ('C17.operation_error', 'reported'),
    ),
    forbid_effect=('C17.operation_result', 'C17.workflow_dispatch', 'semantic_target_substitution'),
    must_precede=(
        (('C17.request', 'admitted'), ('C17.backend_dispatch', 'write')),
        (('C17.backend_dispatch', 'write'), ('C17.partial_effects', 'reported')),
        (('C17.partial_effects', 'reported'), ('C17.operation_error', 'reported')),
    ),
)
```

```python trace
declare_trace_contract(
    action='execute_connector_operation',
    output='request_rejected',
    must_effect=(
        ('C17.request_error', 'reported'),
    ),
    forbid_effect=('C17.backend_dispatch', 'C17.admitted_delta', 'C17.workflow_dispatch', 'semantic_target_substitution'),
)
```

## Details

These cases cover the common connector request. The named direct Subject
lookup and exact values remain governed by the Guarantee. The symbolic
`semantic_target_substitution` effect means changing the caller's logical
target. It does not include private physical binding or explicit Query result
selection. `C17.partial_effects` represents reported known partial effects;
it does not claim that all effects are known.
