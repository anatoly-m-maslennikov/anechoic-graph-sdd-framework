---
identity:
  atom_id: AN-S-1060
context:
  container:
    component: C16
  tier: 2
  lens: QA
state:
  status: active
  version: 23
  updated_at: 2026-10-27 19:59:28 +0400
---
## Summary

Preserve carrier bytes after validation failure

# Preserve carrier bytes after validation failure

## Test case

**Fixture:** run the malformed-filename fixture defined by CA-E-073 **and** compare the complete carrier bytes **before** **and** **after** validation.

**Expected result:** return the malformed-filename failure while preserving byte-identical carrier content.
