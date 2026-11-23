---
atom_family: SPEC
atom_id: AN-S-1523
container:
  component: C16
tier: 4
context:
  lens: QA
state:
  status: archived
  version: 12
  updated_at: 2026-10-23 03:17:34 +0400
---
## Summary

Reject unknown tier

# Reject unknown tier

## Test case

**Fixture:** give an ordinary RMED Atom an unregistered Local Tier token at the registered Local Tier position **in** its otherwise valid filename under CA-D-285; do **not** encode the tier **in** frontmatter.

**Expected result:** fail with the stable unknown-tier diagnostic **and** a non-zero exit.
