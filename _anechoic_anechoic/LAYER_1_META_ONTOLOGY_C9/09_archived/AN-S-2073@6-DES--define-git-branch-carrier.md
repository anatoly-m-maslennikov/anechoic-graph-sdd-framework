---
atom_family: SPEC
atom_id: AN-S-2073
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 6
  updated_at: 2026-11-03 23:25:51 +0400
---
## Summary

Define Git Branch Carrier

## Claim

### Prose Claim

A Git Branch is a repository-owned Carrier identifying a branch head.

### Formal Claim

```CFEL
# model
Carrier/Git Branch
```

## Semantics

A Git Repository contains its Git Branches; this is containment, not specialization.
