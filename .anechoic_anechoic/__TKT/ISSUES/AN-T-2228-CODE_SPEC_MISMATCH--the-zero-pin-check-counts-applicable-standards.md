---
identity:
  atom_id: AN-T-2228
context:
  container:
    component: C45
  tier: 3
  template: Code-Spec Mismatch
state:
  status: active
  version: 1
  updated_at: '2026-11-13T15:59:08.882153+00:00'
---
## Summary

The zero-pin check counts applicable standards

## Concern

CA-M-1015@1 excludes `applies` pins from implementation coverage. The draft test at `APP_WORKBENCH/tests/test_spec_trace_e2e.py` checks zero pins without filtering to `implements`. Its fixture lacks an Applies-only Package, so the check cannot distinguish coverage from applicability.