---
atom_family: SPEC
atom_id: AN-S-198
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

Reject stored scope path

# Reject stored scope path

## Test case

**Fixture:** persist `scope_path` **in** frontmatter **when** the canonical address derives it completely.

**Expected result:** fail with the stable derived-frontmatter-fact diagnostic **and** a non-zero exit.
