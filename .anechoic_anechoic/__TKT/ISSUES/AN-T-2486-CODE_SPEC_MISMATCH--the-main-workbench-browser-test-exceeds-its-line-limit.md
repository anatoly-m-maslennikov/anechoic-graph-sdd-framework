---
atom_family: TKT
atom_id: AN-T-2486
structure:
  container:
    component: C46
  priority: 2
context:
  template: Code-Spec Mismatch
state:
  status: active
  version: 1
  updated_at: '2026-11-13T19:36:58.421506+00:00'
---
## Summary

The main Workbench browser test exceeds its line limit

## Concern

`tests/workbench.e2e.spec.ts` is 518 lines. CA-M-467 sets a mandatory 500-line limit for a frontend file. Split the test along existing scenarios and keep its coverage.
