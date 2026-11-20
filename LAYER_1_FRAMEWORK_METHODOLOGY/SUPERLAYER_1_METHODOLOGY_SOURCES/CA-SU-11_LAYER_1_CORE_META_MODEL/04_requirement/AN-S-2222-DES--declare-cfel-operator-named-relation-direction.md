---
identity:
  atom_id: AN-S-2222
context:
  container:
    component: C9
  tier: 3
  lens: DES
state:
  status: active
  version: 3
  updated_at: '2026-11-13T05:29:21.318804+00:00'
---
## Summary

Declare CFEL operator named Relation direction

## Claim

### Prose Claim

`Source ((RELATION)) Target` is forward and `Target <((RELATION)) Source` is reverse writing of the same canonical Relation fact. Counts stay on written endpoints; reverse normalization swaps canonical Host/Target and count slots. The declared Relation name is matched exactly. This CFEL operator is distinct from the named graph Relation. It grants no inverse permission and creates no second stored fact.
### Formal Claim

```python
# model
set_value(address='Operator//NamedRelationDirection', value='"((RELATION)) / <((RELATION))"')
```

