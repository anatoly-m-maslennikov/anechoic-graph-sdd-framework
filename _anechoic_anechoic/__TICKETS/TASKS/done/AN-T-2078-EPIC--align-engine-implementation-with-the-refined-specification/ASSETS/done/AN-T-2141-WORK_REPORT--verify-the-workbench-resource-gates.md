---
atom_family: TKT
atom_id: AN-T-2141
container:
  atom: AN-T-2078
priority: 2
context:
  template: work_report
state:
  status: done
  version: 1
  updated_at: 2026-11-11 08:17:35 +0400
---

## Summary

Verify the Workbench resource gates

## Details

All nine Docker cases passed against image `sha256:87f745f425bcb3eed2fc8222ff6eaf377d1e6cb6549203cdb6b59bbf342040d2`. Watcher mutations became query-visible in 242.2–316.5 ms on the 5,000-Atom fixture. The 500-Atom and cold-rebuild gates also passed.

The profiler-off soak ran 179 cycles over 1800.00 seconds with the same owner. Peak RAM was 575.2 MiB across all phases, growth above the settled baseline was 43.2 MiB, and idle CPU was 0.027 CPU-seconds over 15 seconds. No OOM kills, retained result tables, pins or watcher work remained. The test used the one-core cap and provides no uncapped peak CPU measurement.

The exact results and limits are in `.anechoic_tmp/CA-P-2791/CA-P-2817/`.
