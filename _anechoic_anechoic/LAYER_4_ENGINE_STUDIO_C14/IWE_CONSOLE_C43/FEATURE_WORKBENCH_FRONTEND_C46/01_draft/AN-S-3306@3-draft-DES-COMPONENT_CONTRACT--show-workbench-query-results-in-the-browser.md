---
atom_family: SPEC
atom_id: AN-S-3306
container:
  component: C46
tier: 0
context:
  template: component_contract
  lens: DES
relations:
  ANSWERS:
  - AN-S-3060
state:
  status: draft
  version: 3
  updated_at: '2026-11-25T10:59:12.783914+00:00'
---
## Summary

Show Workbench query results in the browser

## Guarantee

Open the Workspace of the selected Project before enabling SQL input.
Synchronize pending SQL through the Project HTTP API before running the
current View. Use `view_run` for Run metadata and `view_fetch` for
rows. Fetch rows using the query ID from the completed Run. Display the
returned columns and rows and preserve the editor SQL.

Check displays the verdict for the current SQL and preserves the previous
Run result. Changing SQL clears that Check verdict. Display an error
when the Project API refuses or fails a request, or returns a completed
Run without a query ID. If a completed Run has a save failure, show the
save error, fetch and display the result, and report partial outcome.

## Claim

### Prose Claim

The View Run trace checks that C21 provides a query ID before the browser
displays the completed result. Exact result values, preserved SQL,
and Check behavior remain outside this trace. A partial save trace requires
the query ID and save error, the displayed error, and the completed result.

### Formal Claim

```python trace
declare_trace_contract(
    action='workbench_frontend_run_view',
    output='succeeded',
    must_effect=(('C21.view_run.query_id', 'returned'), ('workbench_display', 'shown')),
    forbid_effect=('C21.view_run.malformed_reply', 'workbench_save_error'),
    must_precede=((('C21.view_run.query_id', 'returned'), ('workbench_display', 'shown')),),
)
```

```python trace
declare_trace_contract(
    action='workbench_frontend_run_view',
    output='partial',
    must_effect=(('C21.view_run.query_id', 'returned'), ('C21.view_run.save_error', 'returned'),
                 ('workbench_save_error', 'shown'), ('workbench_display', 'shown')),
    forbid_effect=('C21.view_run.malformed_reply',),
    must_precede=((('C21.view_run.query_id', 'returned'), ('workbench_display', 'shown')),
                  (('C21.view_run.save_error', 'returned'), ('workbench_save_error', 'shown'))),
)
```
