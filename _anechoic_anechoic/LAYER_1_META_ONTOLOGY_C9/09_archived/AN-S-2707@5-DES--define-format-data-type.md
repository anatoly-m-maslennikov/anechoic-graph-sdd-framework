---
atom_family: SPEC
atom_id: AN-S-2707
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 5
  updated_at: 2026-11-03 23:25:51 +0400
---
## Summary

Define Format Data Type

## Claim

### Prose Claim


Format Data Type names the admissible value domain of a direct Property value.
It is separate from cardinality. The initial vocabulary is provisional; list,
map and reference semantics remain with the governing Format definition.



### Formal Claim

```CFEL
# model
Format.Data Type{::1}:: [string]{::1};

Format.Data Type.*[]{::0}
```

