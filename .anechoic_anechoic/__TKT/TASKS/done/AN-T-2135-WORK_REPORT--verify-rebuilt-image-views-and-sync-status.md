---
identity:
  atom_id: AN-T-2135
context:
  container:
    atom: AN-T-2078
  tier: 4
  template: work_report
state:
  status: done
  version: 1
  updated_at: 2026-11-11 07:44:19 +0400
---

## Summary

Verify rebuilt image Views and sync status

## Details

Image 87f745f425bc passed built-browser flows, shared HTTP/MCP grid checks and result lifetime. Separate disposable gateway checks verified busy and failed capture through both adapters. The browser displayed Syncing and retained the prior local timestamp after the failure with no restart request.

The Compact measurement uses the recovered historical proxy. The exact screenshot build and zoom are unverified. Evidence is under `.anechoic_tmp/CA-P-2791/CA-P-2815/browser-probe/` and the v2 Docker E2E log.
