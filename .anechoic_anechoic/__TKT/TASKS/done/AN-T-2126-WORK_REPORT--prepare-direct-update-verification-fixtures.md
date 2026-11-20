---
identity:
  atom_id: AN-T-2126
context:
  container:
    atom: AN-T-2078
  tier: 4
  template: work_report
state:
  status: done
  version: 1
  updated_at: 2026-11-11 06:58:03 +0400
---

## Summary

Prepare Direct Update verification fixtures

## Details

The disposable Draft, Current and Archived fixtures pin exact identity, Version, Updated At and source and expected readback hashes. The retained parser verified the source and in-memory replacements. Cases also cover invalid values, stale state and duplicate identity.

C730 records the Version and history conflict before a persisted effect can be verified. Evidence: `.anechoic_tmp/CA-P-2791/CA-P-2934/direct-update-fixtures/manifest.json`.
