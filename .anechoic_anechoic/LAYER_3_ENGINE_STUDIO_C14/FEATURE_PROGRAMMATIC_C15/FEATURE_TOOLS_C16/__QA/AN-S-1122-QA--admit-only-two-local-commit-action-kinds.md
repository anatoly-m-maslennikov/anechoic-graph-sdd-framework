---
atom_family: SPEC
atom_id: AN-S-1122
structure:
  container:
    component: C16
  tier: 2
context:
  lens: QA
state:
  status: active
  version: 19
  updated_at: 2026-11-02 19:44:26 +0400
---
## Summary

Admit only two local commit action kinds

# Admit only two local commit action kinds

## Test case

present one valid local real-change commit, one valid local Journal-only commit, **and** separate requests for branch creation, deletion, rename, **or** switch; upstream **or** remote selection **or** configuration; fetch, pull, merge, **or** rebase; push **or** force-push; tag creation; **and** release creation.

## Acceptance criteria

**only** the two commit actions can enter the fenced Git gate. **every** other request is rejected as outside ANECHOIC Tool authority **before** staging, ref mutation, network access, **or** repository-configuration change.
