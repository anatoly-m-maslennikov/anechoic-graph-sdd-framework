---
atom_family: TKT
atom_id: AN-T-2201
container:
  atom: AN-T-2078
priority: 2
context:
  template: work_report
state:
  status: canceled
  version: 1
  updated_at: '2026-11-12T02:41:17.711374+00:00'
---
## Summary

Group DuckDB refreshes for independent lifecycle targets

## Details

Compared two batches of 50 on matching disposable Docker fixtures. Archive used one refresh instead of 50. Promote used two instead of 51, including the load of exact predecessors. The two batches took 13.7 s grouped and 29.0 s ungrouped. The final query showed 50 Current and 50 Archived rows. Focused checks cover dependent targets and publication after a partial failure.

Verified image `sha256:7607f7793de81d53b1d68b31c49ebe97c5dde9d2214b2318b44142dec92599f1`.
