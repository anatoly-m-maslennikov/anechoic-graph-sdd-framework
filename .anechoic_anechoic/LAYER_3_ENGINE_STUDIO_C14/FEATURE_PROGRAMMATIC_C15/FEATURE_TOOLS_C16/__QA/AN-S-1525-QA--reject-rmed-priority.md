---
atom_family: SPEC
atom_id: AN-S-1525
structure:
  container:
    component: C16
  tier: 2
context:
  lens: QA
state:
  status: active
  version: 20
  updated_at: 2026-11-02 19:44:26 +0400
---
## Summary

Reject RMED priority

# Reject RMED priority

## Test case

**Fixture:** add `priority` **to** a tier-classified RMED Atom.

**Expected result:** fail with the stable RMED-priority diagnostic **and** a non-zero exit.
