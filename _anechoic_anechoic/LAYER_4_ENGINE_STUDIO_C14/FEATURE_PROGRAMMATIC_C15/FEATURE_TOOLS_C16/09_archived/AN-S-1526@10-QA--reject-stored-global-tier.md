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
  version: 10
  updated_at: 2026-09-12 04:15:38 +0400
---
## Summary

Reject stored global tier

# Reject stored global tier

## Test case

**Fixture:** persist `global_tier` **in** Atom frontmatter.

**Expected result:** fail with the stable derived-frontmatter-fact diagnostic **and** a non-zero exit.
