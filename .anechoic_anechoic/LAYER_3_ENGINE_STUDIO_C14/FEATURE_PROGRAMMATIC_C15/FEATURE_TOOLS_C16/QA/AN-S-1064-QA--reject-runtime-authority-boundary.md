---
identity:
  atom_id: AN-S-1064
context:
  container:
    component: C16
  tier: 2
  lens: QA
state:
  status: active
  version: 22
  updated_at: 2026-11-02 19:44:26 +0400
---
## Summary

Reject runtime authority boundary

# Reject runtime authority boundary

## Test case

**Fixture:** place the **only** authoritative copy of one active Atom under `.anechoic_runtime`.

**Expected result:** fail with the stable runtime-authority-boundary diagnostic **and** a non-zero exit.
