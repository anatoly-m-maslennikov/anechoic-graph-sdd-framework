---
atom_family: TKT
atom_id: AN-T-2147
structure:
  container:
    atom: AN-T-2078
  priority: 2
context:
  template: work_report
state:
  status: canceled
  version: 1
  updated_at: 2026-11-11 08:58:17 +0400
---

## Summary

Recheck installed Workbench performance

## Details

All three targeted Docker checks passed on the installed 0.4.4.43 image. The 12 watcher mutations became query-visible in 238.7–318.0 ms. The 500-Atom batches, cold index and reread passed their fixed limits. Scope rename took 32.6 seconds against its 60-second limit.

The short guard peaked at 505.0 MiB with no OOM, result table, pin or watcher-work leak. The 30-minute soak is recorded separately in P2960. Evidence is in `.anechoic_tmp/CA-P-2791/CA-P-2817/installed-v5-resource-acceptance.json`.
