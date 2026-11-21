---
atom_family: TKT
atom_id: AN-T-2227
structure:
  container:
    component: C45
  priority: 2
context:
  template: Code-Spec Mismatch
state:
  status: "resolved"
  version: 1
  updated_at: "2026-11-21T00:57:14.990121+00:00"
---
## Summary

Editing a Package trace rereads the subtree

## Concern

CA-M-1015@1 limits ordinary refreshes to affected object and pin rows. In `FEATURE_WORKBENCH_BACKEND/spec_trace.py`, `refresh` maps a Package trace edit to its parent directory, deletes descendant rows, and rescans the entire Package subtree. One pin edit rereads unrelated descendant traces.