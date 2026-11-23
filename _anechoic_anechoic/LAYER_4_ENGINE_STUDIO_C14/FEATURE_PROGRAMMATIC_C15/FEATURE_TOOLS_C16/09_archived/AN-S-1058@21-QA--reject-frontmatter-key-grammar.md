---
atom_family: SPEC
atom_id: AN-S-1058
container:
  component: C16
tier: 2
context:
  lens: QA
state:
  status: archived
  version: 21
  updated_at: 2026-10-27 19:59:28 +0400
---
## Summary

Reject frontmatter key grammar

# Reject frontmatter key grammar

## Test case

**Fixture:** change one registered frontmatter key from `snake_case` **to** another spelling.

**Expected result:** fail with the stable frontmatter-key-grammar diagnostic **and** a non-zero exit.
