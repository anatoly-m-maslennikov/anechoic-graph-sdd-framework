---
atom_family: SPEC
atom_id: AN-S-4886
container:
  component: C34
tier: 0
context:
  template: component_contract
  lens: DES
relations:
  ANSWERS:
  - AN-S-3068
state:
  status: draft
  version: 1
  updated_at: '2026-11-25T00:00:00+00:00'
---

## Summary

Control registered background services.

## Guarantee

`START_BACKGROUND_SERVICES` reads one machine-readable registry from the selected installed release. It exposes status, pause, resume, stop, start and reload for every enabled service. An empty registry is a successful no-op. Reject duplicate or unsafe declarations before mutation.

Use dry-run unless apply is explicit. Repeated apply is idempotent. Preserve accepted inbox, queue, action, receipt, circuit and dead-letter state for every command.

Pause stops new dispatch without deleting accepted intake. Stop stops admission and reaches a declared safe shutdown boundary. Start resumes admission and drains accepted work. Reload reaches a safe boundary, re-resolves the selected installed release, restarts and reconciles preserved work. Do not force termination across an unrecoverable mutation critical section.

Framework implementation is permitted only from `.anechoic_runtime/tools`. Persistent operational state is written only below `.anechoic_runtime`; disposable process staging and cache state only below `.anechoic_tmp`.

Automatic restart and retry remain within declared measured budgets. Exhausted budgets, governance, Journal, staging, ambiguous Git outcome and lease-integrity failures open the circuit or pause autonomous dispatch and require explicit Operator recovery.

## Claim

### Formal Claim

The symbolic `mutation` effect covers mutations relevant to this operation,
including service-state changes. The model distinguishes the stated outcomes;
it does not enumerate registry safety rules or prove implementation behavior.

```python trace
declare_trace_contract(
    action='control_background_services', output='dry_run_reported',
    must_effect=(('release_registry', 'selected'),),
    forbid_effect=('mutation', 'service_state'),
)
```

```python trace
declare_trace_contract(
    action='control_background_services', output='registry_rejected',
    must_effect=(('release_registry', 'selected'), ('registry_validation', 'rejected')),
    forbid_effect=('mutation', 'service_state'),
)
```

```python trace
declare_trace_contract(
    action='control_background_services', output='empty_registry_noop',
    must_effect=(('release_registry', 'selected'),),
    forbid_effect=('mutation', 'service_state'),
)
```

```python trace
declare_trace_contract(
    action='control_background_services', output='apply_reported',
    must_effect=(('release_registry', 'selected'), ('registry_validation', 'passed')),
)
```
