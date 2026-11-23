---
atom_family: SPEC
atom_id: AN-S-1523
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

Reject unknown tier

# Reject unknown tier

## Test case

**Fixture:** give an ordinary RMED Atom an unregistered Local Tier token at the registered Local Tier position **in** its otherwise valid filename under CA-D-285; do **not** encode the tier **in** frontmatter.

**Expected result:** fail with the stable unknown-tier diagnostic **and** a non-zero exit.
