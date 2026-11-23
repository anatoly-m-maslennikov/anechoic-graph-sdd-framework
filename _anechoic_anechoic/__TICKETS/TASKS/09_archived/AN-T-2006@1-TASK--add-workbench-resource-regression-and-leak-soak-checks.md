---
atom_family: TKT
atom_id: AN-T-2006
container:
  component: C43
priority: 2
context:
  template: task
state:
  status: archived
  version: 1
  updated_at: 2026-11-07 16:11:42 +0400
---

## Summary

Add Workbench resource regression and leak soak checks

## Objective

Add and verify the resource and leak checks defined by CA-M-508, CA-E-799 and CA-E-800.

## Tasks

- [x] Create, review and adopt RMED.
- [x] Reuse the applicable Method Policy prompt.
- [ ] Implement and review the accepted RMED.
- [ ] Calibrate and freeze resource limits.
- [ ] Run the resource guard and unchanged performance gates.
- [ ] Run the 30-minute soak and fix confirmed leaks.
- [ ] Record evidence and limitations.
