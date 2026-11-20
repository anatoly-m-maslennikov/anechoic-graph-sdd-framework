---
identity:
  atom_id: AN-S-2237
context:
  container:
    component: C9
  tier: 3
  lens: DES
state:
  status: draft
  version: 2
  updated_at: 2026-11-05 06:30:39 +0400
---
## Summary

Declare CFEL operator alias

## Claim

### Prose Claim

`alias($r) == "notation token"` takes an already bound Relation participant, such as one selected by `$r[<Relation>, (.Name = RELATION_NAME)]`, and binds that declared graph Relation's exact name to one nonempty lexical notation token in the selected effective MODEL. Resolve the name exactly; do not infer case folding or undeclared synonyms. A Relation has at most one authored alias. Reject undeclared Relation names, conflicting alias values and ambiguous token bindings. Without an alias, use the full named Relation notation.

This CFEL operator binds notation metadata; it does not construct a literal-to-Node graph Relation or equate different Relation identities. The token follows the owning Relation Declaration's directional reading and grants no endpoint permission, cardinality or second authored fact. In a graph expression, an already bound Relation participant references that Relation object as an endpoint, whereas `((NAME))` invokes that Relation between endpoints.
### Formal Claim

```python
# model
set_value(address='Operator//Alias', value='"alias($r) == \\"notation token\\""')
```

