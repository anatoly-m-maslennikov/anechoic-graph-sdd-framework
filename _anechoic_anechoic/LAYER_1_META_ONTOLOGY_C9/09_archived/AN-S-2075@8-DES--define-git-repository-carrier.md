---
atom_family: SPEC
atom_id: AN-S-2075
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 8
  updated_at: 2026-11-11 16:04:42 +0400
---
## Summary

Define Git Repository Carrier

## Claim

### Prose Claim

A Git Repository is a Carrier of versioned content and Git references.

### Formal Claim

```CFEL
# model
Carrier/Git Repository ((NARROWER_THAN)) Carrier;
```

## Semantics

Git Repository contains Git Branches; this is containment, not specialization.
