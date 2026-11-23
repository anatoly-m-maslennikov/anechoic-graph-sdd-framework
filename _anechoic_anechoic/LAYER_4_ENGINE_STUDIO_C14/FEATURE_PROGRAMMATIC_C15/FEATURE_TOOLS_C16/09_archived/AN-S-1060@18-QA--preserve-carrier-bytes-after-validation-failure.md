---
atom_family: SPEC
atom_id: AN-S-1060
container:
  component: C16
tier: 2
context:
  lens: QA
state:
  status: archived
  version: 18
  updated_at: 2026-10-24 08:53:16 +0400
---
## Summary

Preserve carrier bytes after validation failure

# Preserve carrier bytes after validation failure

## Test case

**Fixture:** run the malformed-filename fixture defined by CA-E-073 **and** compare the complete carrier bytes **before** **and** **after** validation.

**Expected result:** return the malformed-filename failure while preserving byte-identical carrier content.
