---
atom_family: SPEC
atom_id: AN-S-4884
container:
  component: C18
tier: 0
context:
  template: component_contract
  lens: DES
relations:
  ANSWERS:
  - AN-S-3057
state:
  status: draft
  version: 1
  updated_at: '2026-11-25T00:00:00+00:00'
---

## Summary

Run a Tool Workflow.

## Guarantee

Each public logical Tool operation has exactly one Workflow semantic behavior owner. The owner controls operation sequencing and domain policy. Find, Read, Modify and explicit Create operations remain independent logical operations with their required bindings.

Resolve the unique owner before executing Actions. Reject the request
without executing Actions when no unique owner can be resolved.

A Workflow uses explicit one-target Atom Actions. For several targets, it executes independent Actions in order, stops at the first failed or uncertain Action, retains completed effects and leaves later targets untouched. It makes no cross-Atom all-or-nothing transaction promise.

## Claim

### Formal Claim

These cases cover a Workflow that dispatches Atom Actions.

```python trace
declare_trace_contract(
    action='run_tool_workflow',
    output='workflow_completed',
    must_effect=(('workflow_owner', 'unique_owner_resolved'), ('actions', 'completed')),
    forbid_effect=('action_stop',),
    must_precede=((('workflow_owner', 'unique_owner_resolved'), ('actions', 'completed')),),
)
```

```python trace
declare_trace_contract(
    action='run_tool_workflow',
    output='owner_resolution_failed',
    forbid_effect=('actions',),
)
```

```python trace
declare_trace_contract(
    action='run_tool_workflow',
    output='failed',
    must_effect=(('workflow_owner', 'unique_owner_resolved'), ('actions', 'dispatched'),
                 ('action_stop', 'observed'), ('completed_effects', 'retained'),
                 ('remaining_targets', 'untouched')),
    must_precede=((('workflow_owner', 'unique_owner_resolved'), ('actions', 'dispatched')),
                  (('actions', 'dispatched'), ('action_stop', 'observed')),
                  (('action_stop', 'observed'), ('completed_effects', 'retained')),
                  (('action_stop', 'observed'), ('remaining_targets', 'untouched'))),
)
```
