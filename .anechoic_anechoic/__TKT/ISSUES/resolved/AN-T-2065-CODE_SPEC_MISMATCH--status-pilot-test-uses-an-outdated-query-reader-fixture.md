---
atom_family: TKT
atom_id: AN-T-2065
structure:
  container:
    component: C14
  priority: 2
context:
  template: Code-Spec Mismatch
state:
  status: "resolved"
  version: 1
  updated_at: "2026-11-20T20:35:37.549175+00:00"
---
## Summary

Status pilot test uses an outdated query reader fixture

## Claim

### Prose Claim

CA-E-825@1 requires an acceptance check for the Status pilot. `FEATURE_TOOLS/tests/test_python_status_workflow.py` uses `IndexedReader` from `test_lifecycle_source.py`. That fixture does not implement `lifecycle_contexts`, which the Status path calls to verify the parent. `test_activate_backlog_tree_with_attached_draft` failed with AttributeError. Production Workbench implements the interface.
