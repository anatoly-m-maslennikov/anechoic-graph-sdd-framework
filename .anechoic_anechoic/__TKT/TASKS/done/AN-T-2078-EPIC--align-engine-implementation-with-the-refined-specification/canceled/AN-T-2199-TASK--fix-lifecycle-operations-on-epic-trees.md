---
atom_family: TKT
atom_id: AN-T-2199
structure:
  container:
    atom: AN-T-2078
  priority: 2
context:
  template: task
state:
  status: canceled
  version: 1
  updated_at: '2026-11-12T01:56:22.847434+00:00'
---
## Summary

Fix lifecycle operations on Epic trees

## Objective

Implement and verify the lifecycle follow-up from CA-P-3018.

## Details

- Update the Engine RMEDO and review the affected lifecycle contracts.
- Fix the reported Epic status-change and content-update failures.
- Verify activation of a direct and a nested Task. Test the Draft-child regression independently.
- Record the results in a Work Report.