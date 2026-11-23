---
atom_family: SPEC
atom_id: AN-S-2708
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 6
  updated_at: 2026-11-04 05:21:15 +0400
---
## Summary

Define Format Uniqueness Selection

## Claim

### Prose Claim


Format Uniqueness Selection identifies the comparison population for a
Property uniqueness check. It is optional and does not itself impose
uniqueness. It does not define a notation.



### Formal Claim

```CFEL
# model
Format.Uniqueness Selection:: [string]{::0..1};

Format.Uniqueness Selection.*[]{::0}
```

