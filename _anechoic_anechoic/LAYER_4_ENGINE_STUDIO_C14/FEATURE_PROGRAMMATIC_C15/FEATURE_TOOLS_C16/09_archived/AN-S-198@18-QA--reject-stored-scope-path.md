---
atom_family: SPEC
atom_id: AN-S-198
container:
  component: C16
tier: 2
context:
  lens: QA
state:
  status: archived
  version: 18
  updated_at: 2026-10-25 17:32:27 +0400
---
## Summary

Reject stored scope path

# Reject stored scope path

## Test case

**Fixture:** persist `scope_path` **in** frontmatter **when** the canonical address derives it completely.

**Expected result:** fail with the stable derived-frontmatter-fact diagnostic **and** a non-zero exit.
