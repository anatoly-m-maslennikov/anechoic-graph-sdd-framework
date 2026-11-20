---
identity:
  atom_id: AN-P-37
context:
  container:
    component: C27
  tier: 3
  template: step
state:
  status: active
  version: 11
  updated_at: 2026-11-09 15:54:30 +0400
---

# Summary

Run host-capable Candidate E2E

## Step

This Step invokes CA-O-181 once after CA-O-186's immutable image canary, binding the exact candidate/package/image/N identity and explicit host-capable controller authorization.

## Details

Absent host capability is non-pass, not a fallback to the frozen Docker worker. Failed, partial, stale, unsafe or missing-recording results stop before Full Gate aggregation, promotion and retirement without replay.
