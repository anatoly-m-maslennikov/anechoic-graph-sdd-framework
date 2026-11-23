---
atom_family: SPEC
atom_id: AN-S-3838
container:
  component: C16
tier: 4
context:
  lens: QA
state:
  status: archived
  version: 12
  updated_at: 2026-10-24 00:28:02 +0400
---
## Summary

Permit the imprecise fallback relation in casual scope

# Permit the imprecise fallback relation in casual scope

## Test case

**Fixture:** add the registered imprecise fallback relation **in** a casual scope **where** no precise registered relation applies.

**Expected result:** pass the authority-mode relation check.
