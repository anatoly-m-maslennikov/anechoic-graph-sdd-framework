---
atom_family: SPEC
atom_id: AN-S-4444
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 3
  updated_at: 2026-11-05 06:30:39 +0400
---
## Summary

Declare CONTAINS

## Claim

### Formal Claim

```CFEL
# model
$contains[<Relation>, (.Name = CONTAINS)];
$contained_by[<Relation>, (.Name = IS_CONTAINED_BY)];

$contains <((HAS_INVERSE)) $contained_by;

alias($contains) == "/"
```

## Semantics

CONTAINS relates a Container to its immediately contained part.
