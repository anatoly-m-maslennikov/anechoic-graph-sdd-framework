---
identity:
  atom_id: AN-T-2203
context:
  container:
    atom: AN-T-2078
  tier: 4
  template: work_report
state:
  status: canceled
  version: 1
  updated_at: '2026-11-12T02:41:19.089256+00:00'
---
## Summary

Move Workbench audits off lifecycle responses

## Details

On the ungrouped 50-Atom fixture, synchronous audit work accounted for 0.95 s in Archive and 3.00 s in Promote. The Workbench worker now computes the issue rows in the background and publishes the latest generation. Publishing briefly holds the DuckDB lock. Verified that a blocked audit does not hold a lifecycle response and that the issue tables populate once the audit completes. A full audit finishes once while changed paths queue behind it. The live Update median fell from 8.40 s during repeated full audits to 0.65 s on the final image.

Verified image `sha256:7607f7793de81d53b1d68b31c49ebe97c5dde9d2214b2318b44142dec92599f1`.
