---
atom_family: SPEC
atom_id: AN-S-229
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

Reject non reproducible settings

# Reject non reproducible settings

## Test case

**Fixture:** regenerate Project Settings from unchanged sources **and** obtain different semantic output.

**Expected result:** fail with the stable non-reproducible-settings diagnostic **and** a non-zero exit.
