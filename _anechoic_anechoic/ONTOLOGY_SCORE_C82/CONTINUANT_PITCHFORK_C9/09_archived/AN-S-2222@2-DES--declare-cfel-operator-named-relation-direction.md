---
atom_family: SPEC
atom_id: AN-S-2222
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 2
  updated_at: 2026-11-03 20:00:05 +0400
---
## Summary

Declare CFEL operator named Relation direction

## Claim

### Prose Claim

`Source ((RELATION)) Target` is forward and `Target <((RELATION)) Source` is reverse writing of the same canonical Relation fact. Counts stay on written endpoints; reverse normalization swaps canonical Host/Target and count slots. The declared Relation name is matched exactly. This CFEL operator is distinct from the named graph Relation. It grants no inverse permission and creates no second stored fact.
### Formal Claim

```CFEL
# model
Operator//NamedRelationDirection == "((RELATION)) / <((RELATION))"
```

