---
identity:
  atom_id: AN-T-2155
context:
  container:
    atom: AN-T-2078
  tier: 4
  template: work_report
state:
  status: canceled
  version: 1
  updated_at: 2026-11-11 09:26:28 +0400
---

## Summary

Verify exact Atom lookup limits in Workbench

## Details

Installed query_run returns installed copies for CA-R-1521 and CA-R-3010 even though native carriers exist. The same index omits the exact Archived CA-C-730@6 carrier. The retained exact-path reader is suitable after an authority-bound carrier has been selected. The lifecycle Tool still needs authority-bound logical selection for Current, Draft and Archived Atoms. Evidence is in `.anechoic_tmp/CA-P-2791/CA-P-2934/exact-reference-readback.json`.
