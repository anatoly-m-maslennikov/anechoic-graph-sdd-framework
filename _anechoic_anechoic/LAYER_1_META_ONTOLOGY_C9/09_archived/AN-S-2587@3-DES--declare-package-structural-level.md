---
atom_family: SPEC
atom_id: AN-S-2587
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 3
  updated_at: 2026-11-10 14:38:45 +0400
---

## Summary

Declare Package.structural_level

## Claim

### Formal Claim

```CFEL
# model
Package.structural_level{::1}:: [int]{::1};

Package.structural_level.*[]{::0};

Package.structural_level >= 0;

# instances
Package/Project Package//$implementation.structural_level = 0;

IF (Package//$contained ((IS_CONTAINED_BY)) Package//$container)
THEN ($contained.structural_level = $container.structural_level + 1)
```

