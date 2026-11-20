---
identity:
  atom_id: AN-S-2599
context:
  container:
    component: C9
  tier: 3
  lens: DES
state:
  status: draft
  version: 6
  updated_at: 2026-11-11 05:13:50 +0400
---

## Summary

Declare Workflow

## Claim

### Formal Claim

```python
# model
subject_path(address='Atom/(.Header.Context.Role in (Operations))/Workflow')
relation(source='Workflow', name='NARROWER_THAN', target='Atom/(.Header.Context.Role in (Operations))')
allowed_values(address='Workflow.Header.Context.Form', values=('Workflow',), occurrences='1')
classify(address='Atom/(.Header.Context.Role in (Operations))/Workflow', axis='Container', value='yes', grouped=True)
# instances
relation(source='Workflow//$workflow', name='CONTAINS', target='Step//$step', source_count='1+')
relation(source='Workflow//$workflow_2', name='IS_RUN_BY', target='Step//$step_2', source_count='0+')
relation(source='Workflow//$definition', name='HAS_EXECUTION', target='Workflow Run//$run', source_count='0+')
```

## Semantics

A Workflow defines a graph of Steps for governed work. Its Purpose distinguishes Runtime Workflows from Project Workflows through the selections `Workflow/(.Purpose := Runtime)` and `Workflow/(.Purpose := Project)`.

Both selections inherit the same Step and Action definitions, graph rules, bindings and execution model. Steps and Actions can be reused by either selection. Purpose concerns use in a Project; reusable Workflow definitions can serve different Project-relative purposes without copying their canonical definition. Purpose does not determine shared or isolated execution context, definition ownership or delivery location.
