---
atom_family: TKT
atom_id: AN-T-2148
structure:
  container:
    atom: AN-T-2078
  priority: 2
context:
  template: work_report
state:
  status: canceled
  version: 1
  updated_at: 2026-11-11 08:58:18 +0400
---

## Summary

Prepare Update and Promote Draft evaluations

## Details

Prepared two disposable lifecycle cases. A same-ID Update preserves the predecessor's Resolved status and publishes version 5 from version 4. A many-to-one promotion archives the Current target once, preserves the already Archived target and publishes the Draft.

The pinned inputs and validator are in `.anechoic_tmp/CA-P-2791/CA-P-2934/promotion-fixtures/`. Fixture validation passed. Both cases still need to run through the admitted Tool interface.
