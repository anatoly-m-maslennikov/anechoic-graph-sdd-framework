---
identity:
  atom_id: AN-T-2485
context:
  container:
    component: C45
  tier: 3
  template: Code-Spec Mismatch
state:
  status: active
  version: 1
  updated_at: '2026-11-13T19:36:54.876137+00:00'
---
## Summary

An ordinary Atom refresh walks all indexed Atom rows

## Concern

CA-M-465 requires ordinary Atom changes to avoid a full inventory walk. `service_refresh.py` scans the captured Atom rows for active IDs and rebuilds the source-path set even for a single Atom change. Verify that an ordinary delta updates the affected paths and Archive summary inputs only.
