---
identity:
  atom_id: CA-P-3097
  ref_id: CA-P-3097
context:
  container:
    atom: CA-P-3075
  role: plan
  form: work_report
  topics:
    main_subject: PROJECT STRUCTURE//ANECHOIC
  tier: 3
relations:
  IS_WORK_REPORT_FOR:
  - CA-P-3091
state:
  status: done
  version: 1
  updated_at: '2026-11-18T23:21:25.025177+00:00'
destination:
  file:
    name: CA-P-3097-WORK_REPORT--protect-legacy-local-release-inputs.md
    path: .anechoic_anechoic/03_plan/CA-P-3075-EPIC--apply-the-anechoic-model-to-the-project/020_done
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
