---
atom_family: SPEC
atom_id: AN-S-1964
structure:
  container:
    component: C46
  tier: 5
context:
  lens: QA
state:
  status: draft
  version: 7
  updated_at: '2026-11-14T07:53:35.535093+00:00'
---
## Summary

Verify Workbench read-only result-grid context actions

## Claim

### Prose Claim

Verify read-only result-grid actions in standalone and explicit embedded
Workspaces, using a View with one complete query.

## Details

- Verify the exact grid actions defined by CA-R-2953. Copy and Show full value
  use the complete data even in Limited display.
- Sort and filter across the existing result. Group by one column with
  global counts. Pages stay correct and SQL never reruns.
- Verify approved actions leave the View and result unchanged. Resize, zoom,
  and display preferences affect presentation only.
