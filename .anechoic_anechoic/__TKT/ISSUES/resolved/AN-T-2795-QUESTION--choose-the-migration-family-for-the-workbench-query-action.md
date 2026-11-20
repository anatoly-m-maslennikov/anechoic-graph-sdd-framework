---
atom_family: TKT
atom_id: AN-T-2795
structure:
  container:
    component: C00
  priority: 2
context:
  template: question
state:
  status: resolved
  version: 1
  updated_at: '2026-11-19T13:06:16.239226+00:00'
---
## Summary

Choose the migration family for the Workbench query Action

## Concern

Should the CA-O-240 history use the SPEC family for Workbench read-only queries?

## Details

The 14 retained CA-O-240 revisions define read-only query execution. Twenty Draft Steps point to a CA-O-240 path but describe query checking, preview, and source updates. The replacement Draft CA-O-242 proposes that broader interface. The four parent Draft Workflows have no verified migration family.

The Operator approved migration of the read-only CA-O-240 history as one
SPEC lineage with its original query purpose. This includes the Current
Action and its read-only Draft. Keep the broader CA-O-242 replacement
binding and the conflicting Draft Workflow calls on hold in the migration
receipt.

## References

CA-P-3075, CA-O-240, CA-O-242.
