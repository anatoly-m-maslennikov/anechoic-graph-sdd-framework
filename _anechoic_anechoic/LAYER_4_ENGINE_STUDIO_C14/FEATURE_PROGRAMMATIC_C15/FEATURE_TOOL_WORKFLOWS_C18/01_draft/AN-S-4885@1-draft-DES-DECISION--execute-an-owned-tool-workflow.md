---
atom_family: SPEC
atom_id: AN-S-4885
container:
  component: C18
tier: 1
context:
  template: DECISION
  lens: DES
relations:
  IS_SOLUTION_FOR:
  - AN-S-4884@1-draft
state:
  status: draft
  version: 1
  updated_at: '2026-11-25T00:00:00+00:00'
---

## Summary

Execute an owned Tool Workflow.

## Claim

### Prose Claim

Select one public logical Tool operation and resolve exactly one Workflow semantic behavior owner. The owner sequences explicit target Actions. Each Atom Action affects exactly one explicit Atom target and preserves its own preconditions, source checks and storage-effect safeguards.

Execute the Actions in supplied order. Stop at the first failed or uncertain Action, retain prior completed effects and leave later targets untouched. Report the failure or uncertainty and completed effects. Do not promise a cross-Atom all-or-nothing transaction. Resume and retry policy is not selected here.

### Formal Claim

```python
component_workflow(
    component='C18',
    action='run_tool_workflow',
    machine={
        'id': 'c18_run_tool_workflow',
        'initial': 'idle',
        'states': {
            'idle': {'on': {
                'tool_workflow_requested': {'target': 'resolving', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'trigger'}}},
            }},
            'resolving': {'on': {
                'unique_owner_resolved': {'target': 'executing', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'effect', 'target': 'workflow_owner', 'outcome': 'unique_owner_resolved'}}},
                'owner_resolution_failed': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'owner_resolution_failed'}}},
            }},
            'executing': {'on': {
                'action_dispatched': {'target': 'waiting', 'guard': {'type': 'matchesTrace', 'params': {
                    'kind': 'effect', 'target': 'actions', 'outcome': 'dispatched',
                    'detail': {'target_count': 1, 'explicit': True, 'sequence': 'next_supplied_target'},
                }}},
                'actions_completed': {'target': 'reporting', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'effect', 'target': 'actions', 'outcome': 'completed'}}},
            }},
            'waiting': {'on': {
                'action_confirmed': {'target': 'executing', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'effect', 'target': 'action_result', 'outcome': 'confirmed'}}},
                'action_failed_or_uncertain': {'target': 'retaining', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'effect', 'target': 'action_stop', 'outcome': 'observed'}}},
            }},
            'retaining': {'on': {
                'completed_effects_retained': {'target': 'protecting_remaining', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'effect', 'target': 'completed_effects', 'outcome': 'retained'}}},
            }},
            'protecting_remaining': {'on': {
                'remaining_targets_untouched': {'target': 'reporting_failure', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'effect', 'target': 'remaining_targets', 'outcome': 'untouched'}}},
            }},
            'reporting_failure': {'on': {
                'workflow_failed': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'reporting': {'on': {
                'workflow_completed': {'target': 'completed', 'guard': {'type': 'matchesTrace',
                    'params': {'kind': 'output', 'outcome': 'workflow_completed'}}},
            }},
            'completed': {'type': 'final'},
            'failed': {'type': 'final'},
        },
    },
)
```
