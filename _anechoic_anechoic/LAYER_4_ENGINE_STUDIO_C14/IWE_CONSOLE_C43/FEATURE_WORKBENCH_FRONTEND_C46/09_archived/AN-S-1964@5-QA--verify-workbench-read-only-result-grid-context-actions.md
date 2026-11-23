---
atom_family: SPEC
atom_id: AN-S-1964
container:
  component: C46
tier: 5
context:
  lens: QA
state:
  status: archived
  version: 5
  updated_at: 2026-11-10 20:47:54 +0400
---
## Summary

Verify Workbench read-only result-grid context actions

## Claim scope

The Workbench frontend's read-only result grid and its global filter, sort and grouping interactions.

## Claim

### Prose Claim

In standalone and explicit embedded context, open a Tab containing a SQL script and verify equivalent read-only grid behavior through each Workspace/View identity. Complete materialized values remain available even under Limited display. Expose exactly Cell Copy value, Cell Show full value, Row Copy row, Column Sort ascending/descending, Group by, Filter and Clear filter; copy/show preserve full selected data and none mutates View/result.

Sort/filter operate globally over complete cache and pages remain correct without rerunning SQL. Group exactly one selected column with global counts; no nested group, pivot, export, collaboration or editor action appears in this menu (shared file delivery remains outside it). Adaptive/Fixed/Full/Limited, resize and zoom stay display-only. Pass only when every approved action has this behavior and no unsupported feature/replay appears.
