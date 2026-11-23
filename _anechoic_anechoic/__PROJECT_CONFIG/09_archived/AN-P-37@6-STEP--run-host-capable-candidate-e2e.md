---
atom_family: PROJECT_CONFIG
atom_id: AN-P-37
structure:
  container:
    component: C00
context:
  template: step
state:
  status: archived
  version: 6
  updated_at: 2026-10-24 11:29:41 +0400
---
## Summary

Run host-capable Candidate E2E

# Summary

Run host-capable Candidate E2E

## Step

This Step invokes CA-O-181 once after CA-O-186's immutable image canary, binding the exact candidate/package/image/N identity and explicit host-capable controller authorization.

## Details

Absent host capability is non-pass, not a fallback to the frozen Docker worker. Failed, partial, stale, unsafe or missing-recording results stop before Full Gate aggregation, promotion and retirement without replay.
