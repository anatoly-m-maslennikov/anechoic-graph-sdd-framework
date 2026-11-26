---
atom_family: SPEC
atom_id: AN-S-3305
container:
  component: C59
tier: 0
context:
  template: component_contract
  lens: SPEC
relations:
  ANSWERS:
  - AN-S-3047
state:
  status: draft
  version: 3
  updated_at: '2026-11-25T10:58:34Z'
---
## Summary

Own one Project database

## Guarantee

Admit one Project instance and its Manifest revision before opening
the Workbench database. Keep the connection, projection transactions,
and result snapshots in the Kernel process.

Execute the admitted database operations for that Project over the
declared private API. Reject calls for a different instance. Preserve
committed projection and result state when an operation fails.

## Claim

### Formal Claim

The selected successful unsaved query requires the admitted Project binding,
a selected statement, and a retained result before delivery. It also
requires an attempt to enqueue the query log; successful logging is not
required for a usable result.

```python trace
declare_trace_contract(
    action='kernel_run_query',
    interface='database_api',
    transport='http',
    route='POST /database',
    operation='operation',
    output='succeeded',
    must_effect=(('C59.project_binding', 'admitted'),
                 ('C59.statement', 'selected'),
                 ('C59.result', 'retained'),
                 ('C59.query_log', 'enqueue_attempted')),
    must_precede=((('C59.project_binding', 'admitted'), ('C59.statement', 'selected')),
                  (('C59.statement', 'selected'), ('C59.result', 'retained')),
                  (('C59.result', 'retained'), ('C59.query_log', 'enqueue_attempted'))),
)
```

A foreign Project binding is rejected before statement selection or result retention.

```python trace
declare_trace_contract(
    action='kernel_run_query',
    interface='database_api',
    transport='http',
    route='POST /database',
    operation='operation',
    output='rejected',
    must_effect=(('C59.project_binding', 'rejected'),),
    forbid_effect=('C59.statement', 'C59.result'),
)
```

These traces cover the selected unsaved query and foreign-binding rejection.
They do not establish result correctness, transaction recovery, or successful
logging. Trace conformance requires recorded evidence. The route label
`operation` does not define exact request operation names.

## References

AN-S-3047, AN-S-1363, and AN-T-2947.
