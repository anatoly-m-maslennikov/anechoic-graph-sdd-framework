---
atom_family: SPEC
atom_id: AN-S-4351
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 1
  updated_at: 2026-11-10 14:38:45 +0400
---

## Summary

Declare Project Package

## Claim

### Formal Claim

```CFEL
# model
Package/Project Package;

# instances
Package/Project Package//$package{::1};

Package/Project Package//$package_2 {::0}((IS_CONTAINED_BY)) Package//$package_3
```

## Semantics

The Project Package is the root Package of a Project's implementation.
