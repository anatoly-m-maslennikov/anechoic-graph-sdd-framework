---
atom_family: TKT
atom_id: AN-T-1816
structure:
  container:
    atom: AN-T-1818
  priority: 2
context:
  template: task
  label: Subtask
state:
  status: done
  version: 2
  updated_at: 2026-11-09 01:40:38 +0400
---

## Summary

Fix moved-directory indexing

## Details

1. Reproduce the large-move failure (15 min).
2. Correct affected-subtree handling and add its regression (20 min).
3. Review and fix boundary handling (10 min).
4. Verify the performance gate and release (20 min).
