---
atom_family: SPEC
atom_id: AN-S-2025
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 4
  updated_at: 2026-11-02 18:21:51 +0400
---
## Summary

Declare Aspect

## Claim

### Prose Claim



- MODEL declares the generic Aspect.
- All concrete Aspects are instances in the applicable PROJECT STRUCTURE tree.

### Formal Claim

```CFEL
# model
Aspect;

Aspect ((NARROWER_THAN)) Node
```

## Semantics

An Aspect is a topic through which an Atom addresses its Subject.
