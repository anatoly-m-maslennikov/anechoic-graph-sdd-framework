---
atom_family: SPEC
atom_id: AN-S-229
container:
  component: C16
tier: 2
context:
  lens: QA
state:
  status: archived
  version: 19
  updated_at: 2026-10-27 19:59:29 +0400
---
## Summary

Reject non reproducible settings

# Reject non reproducible settings

## Test case

**Fixture:** regenerate Project Settings from unchanged sources **and** obtain different semantic output.

**Expected result:** fail with the stable non-reproducible-settings diagnostic **and** a non-zero exit.
