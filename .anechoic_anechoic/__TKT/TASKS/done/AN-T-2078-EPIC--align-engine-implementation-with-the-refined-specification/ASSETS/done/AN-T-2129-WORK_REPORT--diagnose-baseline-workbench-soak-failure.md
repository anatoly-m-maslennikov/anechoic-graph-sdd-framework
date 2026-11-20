---
atom_family: TKT
atom_id: AN-T-2129
structure:
  container:
    atom: AN-T-2078
  priority: 2
context:
  template: work_report
state:
  status: done
  version: 1
  updated_at: 2026-11-11 07:15:01 +0400
---

## Summary

Diagnose baseline Workbench soak failure

## Details

The d520 soak failed its frozen memory guard after about 21 minutes. Last reported sample at cycle 120 was 554 MiB current and 605 MiB peak. Source and relation inventories, result ownership, threads and file descriptors remained stable. The next Scope Declaration refresh rebuilt 5,000 rows before the failure.

The runner now reports the exact failing sample. The diagnostic will distinguish process allocations from file cache. Evidence: `.anechoic_tmp/CA-P-2791/CA-P-2817/soak-baseline-failure.json`.
