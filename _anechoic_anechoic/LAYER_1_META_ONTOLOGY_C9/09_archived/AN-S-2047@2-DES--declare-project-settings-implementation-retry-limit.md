---
atom_family: SPEC
atom_id: AN-S-2047
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 2
  updated_at: 2026-11-04 05:21:15 +0400
---

## Summary

Declare Project.Settings.Implementation Retry Limit

## Claim

### Prose Claim


An omitted value follows the governed default resolution. A value is an integer at least zero. Zero permits no retries after the initial failure. The limit does not grant repair permission or bypass authority or confidence rules.

### Formal Claim

```CFEL
# model
Project.Settings.Implementation Retry Limit:: [int]{::0..1};

Project.Settings.Implementation Retry Limit.*[]{::0}
```

