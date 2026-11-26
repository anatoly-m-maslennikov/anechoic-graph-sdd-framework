---
atom_family: SPEC
atom_id: AN-S-4889
container:
  component: C35
tier: 1
context:
  template: DECISION
  lens: DES
relations:
  IS_SOLUTION_FOR:
  - AN-S-4888@1-draft
state:
  status: draft
  version: 1
  updated_at: '2026-11-25T00:00:00+00:00'
---

## Summary

Replace selected logical Atom Properties.

## Claim

### Prose Claim

Admit exactly one explicit Atom target before Find. Reject zero, multiple or implicit targets before selection or change. Find selects one explicit Atom target and its current values within the explicit frontier. Check the expected state separately. Compute the full new value and pass the exact identity, expected state, logical Property or section and old and new values to Change. Preserve unselected content. Summary and Type changes use the existing fresh-ID replacement path.

Report completion, failure or uncertainty for this target. The C18
Workflow coordinates Actions across targets.

### Formal Claim

```python
component_workflow(
    component='C35',
    action='replace_logical_atom_properties',
    machine={
        'id': 'c35_replace_logical_atom_properties',
        'initial': 'idle',
        'states': {
            'idle': {'on': {
                'replacement_requested': {'target': 'admitting', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'trigger'}}},
            }},
            'admitting': {'on': {
                'explicit_target_admitted': {'target': 'selecting', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'effect', 'target': 'logical_target', 'outcome': 'one_explicit', 'detail': {'target_count': 1, 'explicit': True}}}},
                'invalid_target': {'target': 'reporting_invalid_target', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'effect', 'target': 'logical_target', 'outcome': 'invalid_cardinality'}}},
            }},
            'selecting': {'on': {
                'target_selected': {'target': 'checking', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'effect', 'target': 'selected_atom_value', 'outcome': 'read'}}},
                'selection_failed': {'target': 'reporting_failure', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'effect', 'target': 'logical_target', 'outcome': 'failed'}}},
                'selection_uncertain': {'target': 'reporting_uncertainty', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'effect', 'target': 'logical_target', 'outcome': 'uncertain'}}},
            }},
            'checking': {'on': {
                'state_checked': {'target': 'preparing_change', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'effect', 'target': 'expected_state', 'outcome': 'checked'}}},
                'state_mismatch': {'target': 'reporting_stale', 'guard': {'type': 'matchesTrace',
                    'params': {'kind': 'effect', 'target': 'expected_state', 'outcome': 'mismatch'}}},
                'check_failed': {'target': 'reporting_failure', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'effect', 'target': 'expected_state', 'outcome': 'failed'}}},
                'check_uncertain': {'target': 'reporting_uncertainty', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'effect', 'target': 'expected_state', 'outcome': 'uncertain'}}},
            }},
            'preparing_change': {'on': {
                'old_and_new_supplied': {'target': 'changing', 'guard': {'type': 'matchesTrace',
                    'params': {'kind': 'effect', 'target': 'logical_value_delta',
                               'outcome': 'complete_old_and_new_supplied'}}},
            }},
            'changing': {'on': {
                'change_completed': {'target': 'preserving_unselected', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'effect', 'target': 'change', 'outcome': 'completed'}}},
                'change_failed': {'target': 'reporting_failure', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'effect', 'target': 'change', 'outcome': 'failed'}}},
                'change_uncertain': {'target': 'reporting_uncertainty', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'effect', 'target': 'change', 'outcome': 'uncertain'}}},
            }},
            'preserving_unselected': {'on': {
                'unselected_values_preserved': {'target': 'reporting', 'guard': {'type': 'matchesTrace',
                    'params': {'kind': 'effect', 'target': 'unselected_content', 'outcome': 'preserved'}}},
            }},
            'reporting': {'on': {
                'change_reported': {'target': 'completed', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'output', 'outcome': 'change_reported'}}},
            }},
            'reporting_invalid_target': {'on': {
                'invalid_target_rejected': {'target': 'stopped', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'output', 'outcome': 'invalid_target_rejected'}}},
            }},
            'reporting_stale': {'on': {
                'stale_precondition_rejected': {'target': 'stopped', 'guard': {'type': 'matchesTrace',
                    'params': {'kind': 'output', 'outcome': 'stale_precondition_rejected'}}},
            }},
            'reporting_failure': {'on': {
                'failure_recorded': {'target': 'failure_output', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'effect', 'target': 'replacement_report', 'outcome': 'failure'}}},
            }},
            'failure_output': {'on': {
                'failure_reported': {'target': 'stopped', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'output', 'outcome': 'failure_reported'}}},
            }},
            'reporting_uncertainty': {'on': {
                'uncertainty_recorded': {'target': 'uncertainty_output', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'effect', 'target': 'replacement_report', 'outcome': 'uncertainty'}}},
            }},
            'uncertainty_output': {'on': {
                'uncertainty_reported': {'target': 'stopped', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'output', 'outcome': 'uncertainty_reported'}}},
            }},
            'completed': {'type': 'final'},
            'stopped': {'type': 'final'},
        },
    },
)
```
