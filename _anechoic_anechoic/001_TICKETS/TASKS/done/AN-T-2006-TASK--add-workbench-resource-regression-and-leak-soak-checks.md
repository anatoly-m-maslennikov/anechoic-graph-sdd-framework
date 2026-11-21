---
atom_family: TKT
atom_id: AN-T-2006
container:
  component: C43
priority: 2
context:
  template: task
state:
  status: done
  version: 3
  updated_at: 2026-11-07 14:47:29 +0000
---

## Summary

Add Workbench resource regression and leak soak checks

## Objective

Add and verify the resource and leak checks defined by CA-M-508, CA-E-799 and CA-E-800.

## Tasks

- [x] Create, review and adopt RMED.
- [x] Reuse the applicable Method Policy prompt.
- [x] Implement and review the accepted RMED.
- [x] Calibrate and freeze resource limits.
- [x] Run the resource guard and unchanged performance gates.
- [x] Run the 30-minute soak and fix confirmed leaks.
- [x] Record evidence and limitations.

## Results

Completed. See [acceptance report](CA-P-2714-TASK--add-workbench-resource-regression-and-leak-soak-checks/report.md). The resource-test pass did not deploy changes. The subsequent local release installed and verified version 0.4.4.35; see the linked report.
