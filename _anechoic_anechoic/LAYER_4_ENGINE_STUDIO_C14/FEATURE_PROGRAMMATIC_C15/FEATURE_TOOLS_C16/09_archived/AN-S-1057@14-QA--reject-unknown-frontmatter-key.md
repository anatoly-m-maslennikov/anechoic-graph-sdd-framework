---
atom_family: SPEC
atom_id: AN-S-1057
container:
  component: C16
tier: 4
context:
  lens: QA
state:
  status: archived
  version: 14
  updated_at: 2026-10-24 01:18:03 +0400
---
## Summary

Reject unknown frontmatter key

# Reject unknown frontmatter key

## Test case

**Fixture:** add one unregistered frontmatter key.

**Expected result:** fail with the stable unknown-frontmatter-key diagnostic **and** a non-zero exit.
