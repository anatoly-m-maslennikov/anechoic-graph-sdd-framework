---
identity:
  atom_id: AN-T-2065
context:
  container:
    component: C14
  tier: 4
  template: Code-Spec Mismatch
state:
  status: active
  version: 1
  updated_at: '2026-11-12T12:58:58.940667+00:00'
---
## Summary

Status pilot test uses an outdated query reader fixture

## Claim

### Prose Claim

CA-E-825@1 requires an acceptance check for the Status pilot. `FEATURE_TOOLS/tests/test_python_status_workflow.py` uses `IndexedReader` from `test_lifecycle_source.py`. That fixture does not implement `lifecycle_contexts`, which the Status path calls to verify the parent. `test_activate_backlog_tree_with_attached_draft` failed with AttributeError. Production Workbench implements the interface.
