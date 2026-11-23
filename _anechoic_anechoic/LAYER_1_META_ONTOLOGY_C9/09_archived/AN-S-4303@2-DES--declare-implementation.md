---
atom_family: SPEC
atom_id: AN-S-4303
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 2
  updated_at: 2026-11-02 00:18:22 +0400
---

## Summary

Declare Implementation

## Claim

### Formal Claim

```CFEL
# model
Package/Implementation;

# instances
Package/Implementation//$package{::1};

Package/Implementation//$package_2 {::0}((IS_CONTAINED_BY)) Package//$package_3
```

## Semantics

The root Package of a Project's implementation.
