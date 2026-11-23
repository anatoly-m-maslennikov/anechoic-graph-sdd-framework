---
atom_family: SPEC
atom_id: AN-S-1525
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

Reject RMED priority

# Reject RMED priority

## Test case

**Fixture:** add `priority` **to** a tier-classified RMED Atom.

**Expected result:** fail with the stable RMED-priority diagnostic **and** a non-zero exit.
