---
atom_family: TKT
atom_id: AN-T-2228
structure:
  container:
    component: C45
  priority: 2
context:
  template: Code-Spec Mismatch
state:
  status: "resolved"
  version: 1
  updated_at: "2026-11-20T20:36:34.864552+00:00"
---
## Summary

The zero-pin check counts applicable standards

## Concern

CA-M-1015@1 excludes `applies` pins from implementation coverage. The draft test at `APP_WORKBENCH/tests/test_spec_trace_e2e.py` checks zero pins without filtering to `implements`. Its fixture lacks an Applies-only Package, so the check cannot distinguish coverage from applicability.