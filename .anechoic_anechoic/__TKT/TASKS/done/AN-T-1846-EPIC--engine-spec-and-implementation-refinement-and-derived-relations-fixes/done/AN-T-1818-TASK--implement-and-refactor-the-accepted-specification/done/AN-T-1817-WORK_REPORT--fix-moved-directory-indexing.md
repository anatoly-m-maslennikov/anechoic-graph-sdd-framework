---
atom_family: TKT
atom_id: AN-T-1817
structure:
  container:
    atom: AN-T-1818
  priority: 2
context:
  template: work_report
state:
  status: done
  version: 2
  updated_at: 2026-11-09 01:40:38 +0400
---

## Summary

Fix moved-directory indexing

## Details

The destination-directory watcher fix covers both native directory flags and misreported flags, while refusing traversal outside the source root. Eleven watcher tests and the full 5,000-plus-500 Docker gate pass: batch move 8.128 seconds; 12 watcher mutations 240.0–340.6 ms. No gate was relaxed and the 500-Atom real benchmark corpus was preserved. Final deployment/live canary remain P2731.
