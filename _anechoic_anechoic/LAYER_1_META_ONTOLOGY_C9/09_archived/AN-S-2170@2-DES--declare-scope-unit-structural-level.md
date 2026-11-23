---
atom_family: SPEC
atom_id: AN-S-2170
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

Declare Scope Unit.structural_level

## Claim

### Formal Claim

```CFEL
# model
Scope Unit.structural_level{::1}:: [int]{::1};

Scope Unit.structural_level.*[]{::0};

Scope Unit.structural_level >= 0;

# instances
Scope Unit/Project//$project.structural_level = 0;

IF (Scope Unit//$contained ((IS_CONTAINED_BY)) Scope Unit//$container)
THEN ($contained.structural_level = $container.structural_level + 1)
```

