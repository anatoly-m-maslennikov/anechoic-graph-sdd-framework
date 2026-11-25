---
atom_family: SPEC
atom_id: AN-S-4794
container:
  component: C43
tier: 0
context:
  template: component_contract
  lens: DES
relations:
  ANSWERS:
  - AN-S-3046
state:
  status: draft
  version: 2
  updated_at: '2026-11-25T10:59:12.771063+00:00'
---

## Summary

Provide a Project Workbench

## Guarantee

Provide a browser Workspace for an admitted Project and expose its Workbench
operations through the Project interface. A View holds SQL and its result;
Run and Check use the selected Project. Report failed operations to the caller.

The browser maintains local drafts and display preferences. The Backend owns
Project operation dispatch; the Kernel owns query execution and projection.
Saved items and transient results follow their respective owners' lifetimes.
Provide the Workbench MCP App resource and the static Realization Graph through
their respective Components.

## Claim

### Prose Claim

For a successful View Run, the trace records the query ID returned by C21
before C46 displays the result, with no displayed save error. If the Run completes
but Save fails, the trace records the query ID and save error from C21, then C46
displays the save error and result and reports a partial outcome.

The trace does not establish the returned columns or rows, preserved SQL,
Check behavior, or the other guarantees above.

### Formal Claim

```python trace
declare_trace_contract(
    action='workbench_run_view',
    output='succeeded',
    must_effect=(('C21.view_run.query_id', 'returned'), ('workbench_display', 'shown')),
    forbid_effect=('workbench_save_error',),
    must_precede=((('C21.view_run.query_id', 'returned'), ('workbench_display', 'shown')),),
)
```

```python trace
declare_trace_contract(
    action='workbench_run_view',
    output='partial',
    must_effect=(('C21.view_run.query_id', 'returned'), ('C21.view_run.save_error', 'returned'),
                 ('workbench_save_error', 'shown'), ('workbench_display', 'shown')),
    must_precede=((('C21.view_run.query_id', 'returned'), ('C21.view_run.save_error', 'returned')),
                  (('C21.view_run.save_error', 'returned'), ('workbench_save_error', 'shown')),
                  (('workbench_save_error', 'shown'), ('workbench_display', 'shown'))),
)
```

```python trace
declare_trace_contract(
    action='workbench_run_view',
    output='failed',
    must_effect=(('workbench_run_failure', 'reported'),),
)
```
