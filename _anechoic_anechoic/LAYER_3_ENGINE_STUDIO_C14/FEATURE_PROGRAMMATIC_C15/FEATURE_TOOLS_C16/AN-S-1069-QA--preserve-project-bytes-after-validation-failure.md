---
atom_family: SPEC
atom_id: AN-S-1069
container:
  component: C16
tier: 2
context:
  lens: QA
state:
  status: active
  version: 22
  updated_at: 2026-10-27 19:59:29 +0400
---
## Summary

Preserve project bytes after validation failure

# Preserve project bytes after validation failure

## Test case

**Fixture:** run the missing-relation-target fixture defined by CA-E-104 **and** compare **all** project bytes **before** **and** **after** validation.

**Expected result:** return the missing-relation-target failure while preserving byte-identical project content.
