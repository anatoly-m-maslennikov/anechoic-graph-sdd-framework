---
atom_family: SPEC
atom_id: AN-S-2072
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 7
  updated_at: 2026-11-11 16:04:42 +0400
---
## Summary

Define Git Commit Carrier

## Claim

### Prose Claim

A Git Commit is an immutable Carrier representing a committed repository snapshot and its commit metadata.

### Formal Claim

```CFEL
# model
Carrier/Git Commit ((NARROWER_THAN)) Carrier;
```

## Semantics

Its native identity is interpreted within its repository context. Author, signer and source facts remain provenance.
