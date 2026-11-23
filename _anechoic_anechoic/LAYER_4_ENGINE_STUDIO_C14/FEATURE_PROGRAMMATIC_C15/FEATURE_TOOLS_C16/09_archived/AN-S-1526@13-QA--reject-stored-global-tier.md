---
atom_family: SPEC
atom_id: AN-S-1526
container:
  component: C16
tier: 4
context:
  lens: QA
state:
  status: archived
  version: 13
  updated_at: 2026-10-24 00:51:05 +0400
---
## Summary

Reject stored global tier

# Reject stored global tier

## Test case

**Fixture:** persist `global_tier` **in** Atom frontmatter.

**Expected result:** fail with the stable derived-frontmatter-fact diagnostic **and** a non-zero exit.
