---
atom_family: SPEC
atom_id: AN-S-2197
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 3
  updated_at: 2026-11-04 07:51:19 +0400
---
## Summary

Declare Projection.ID

## Claim

### Formal Claim

```CFEL
# model
Projection.ID{::1}:: [string]{::1};

Projection.ID.*[]{::0};

# instances
DETERMINES(Projection//$projection, (.Form, .Scope Unit), (.ID));

DETERMINES(Projection//$projection_2, (.ID), (.Form, .Scope Unit))
```

