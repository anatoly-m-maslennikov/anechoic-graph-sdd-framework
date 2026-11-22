---
atom_family: TKT
atom_id: AN-T-2124
container:
  atom: AN-T-2078
priority: 2
context:
  template: work_report
state:
  status: done
  version: 1
  updated_at: 2026-11-11 06:50:39 +0400
---

## Summary

Verify browser partial Bookmark save

## Details

Image d520960c81eb preserved the completed result, dirty indicator and prior Bookmark ID and URL when the read-only Journal rejected Save. The browser showed the save error and rendered untrusted cell markup as text.

Evidence: `.anechoic_tmp/CA-P-2791/CA-P-2815/browser-probe/browser-probe-2.log`.
