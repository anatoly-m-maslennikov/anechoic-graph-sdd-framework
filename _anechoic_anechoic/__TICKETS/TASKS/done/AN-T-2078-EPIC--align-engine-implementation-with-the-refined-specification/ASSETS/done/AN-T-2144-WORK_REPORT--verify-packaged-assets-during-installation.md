---
atom_family: TKT
atom_id: AN-T-2144
container:
  atom: AN-T-2078
priority: 2
context:
  template: work_report
state:
  status: done
  version: 1
  updated_at: 2026-11-11 08:43:36 +0400
---

## Summary

Verify packaged assets during installation

## Details

The v4 image passed its build. Installed verification stopped because it recompiled the schema and relation registry after copying the derived Framework. The new bytes differed from the exact candidate's packaged assets.

No-build verification now checks the packaged assets against the immutable image. The release checks that match before replacing the installed Framework or runtime. The corrected verifier accepted the exact v4 image after the copy. Focused tests cover changed, missing and unsafe assets. Evidence is under `.anechoic_tmp/CA-P-2791/CA-P-2818/release-preflight/`.
