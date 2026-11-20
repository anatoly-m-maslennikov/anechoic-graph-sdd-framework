---
identity:
  atom_id: AN-S-1057
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

Reject unknown frontmatter key

# Reject unknown frontmatter key

## Test case

**Fixture:** add one unregistered frontmatter key.

**Expected result:** fail with the stable unknown-frontmatter-key diagnostic **and** a non-zero exit.
