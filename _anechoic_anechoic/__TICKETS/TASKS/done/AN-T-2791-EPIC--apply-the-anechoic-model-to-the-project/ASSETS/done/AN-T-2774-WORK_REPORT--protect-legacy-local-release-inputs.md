---
atom_family: TKT
atom_id: AN-T-2774
container:
  atom: AN-T-2791
priority: 2
context:
  template: work_report
state:
  status: done
  version: 1
  updated_at: '2026-11-18T23:21:25.025177+00:00'
---
## Summary

Protect legacy Local Release inputs

## Details

The protected baseline contains 1,108 selected records plus settings,
Scope Unit declarations, Local Release Workflow CA-O-164@37, and the
callback selector. The Workflow uses bare Step and Action IDs. The baseline
records the observed versions and digests for each selected carrier.
A second selection found no path or digest changes.

Package selection excludes a parallel `.anechoic_*` records directory
at the Project root. The coexistence fixture uses `.anechoic_anechoic`
beside legacy `.anechoic_anechoic` and verifies legacy source parity.
The 36 Local Release unit tests passed.

Evidence is in `.anechoic_tmp/anechoic-apply-3075/release/`.
CA-P-3095 owns the clean isolated rebuild after batch application.
