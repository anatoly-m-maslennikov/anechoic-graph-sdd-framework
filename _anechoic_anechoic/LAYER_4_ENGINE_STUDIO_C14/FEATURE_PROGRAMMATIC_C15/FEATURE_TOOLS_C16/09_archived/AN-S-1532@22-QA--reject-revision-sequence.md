---
atom_family: SPEC
atom_id: AN-S-1532
container:
  component: C16
tier: 2
context:
  lens: QA
state:
  status: archived
  version: 22
  updated_at: 2026-10-27 06:04:45 +0400
---
## Summary

Reject revision sequence

# Reject revision sequence

## Test case

**Fixture:** give an Atom a successive Revision whose Version does **not** increase under CA-R-1415. include a formatting-only Revision with an increased Version **and** the exact preceding Updated At value as a control under CA-R-1492.

**Expected result:** fail the non-increasing Version with the stable revision-sequence diagnostic **and** a non-zero exit. do **not** fail the formatting-only control because Updated At is unchanged. preserve other applicable Revision checks **without** treating a semantic change as formatting.
