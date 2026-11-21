---
atom_family: TKT
atom_id: AN-T-1827
container:
  atom: AN-T-1846
priority: 2
context:
  template: work_report
state:
  status: done
  version: 4
  updated_at: 2026-11-09 01:40:38 +0400
---

## Summary

Expose missing declared Content through query_run

## Details

Operation Declaration and reader corrections expose the supported declared Content through query_run. The 78 unavailable legacy Atoms remain explicitly deferred. The new literal schema generator reads Current Header and Content Declarations; Mode 2 remains factual Headers plus declared Content. No atom_document or raw-source SQL escape was added.
