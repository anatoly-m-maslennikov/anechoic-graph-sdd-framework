---
atom_family: SPEC
atom_id: AN-S-1466
container:
  component: C15
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 1
  updated_at: 2026-11-11 05:51:23 +0400
---

## Summary

Verify fixed runtime code and schemas

## Claim

### Prose Claim

Change code or a declaration while a service is running. Verify that its code and compiled contracts stay fixed through normal data refresh and full reread. Start the rebuilt image and verify that it applies the change. Verify that source-data synchronization continues with the current contracts and that an invalid generated artifact produces an explicit error.
