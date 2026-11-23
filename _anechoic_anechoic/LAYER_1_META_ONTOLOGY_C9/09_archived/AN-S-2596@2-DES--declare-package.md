---
atom_family: SPEC
atom_id: AN-S-2596
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

Declare Package

## Claim

### Formal Claim

```CFEL
# model
Package >| (Container == yes);

Package ((NARROWER_THAN)) Continuant;

# instances
Package//$package_2{::0..1}((IS_CONTAINED_BY)) Package//$package_3;

Package//$package_4{::0+}((CONTAINS)) Package//$package_5;

IF (Package//$package not in (Package/Implementation//$package_6))
THEN ($package {==1}((IS_CONTAINED_BY)) Package//$package_7);
```

## Semantics

A logical collection of implementation and documentation parts.
