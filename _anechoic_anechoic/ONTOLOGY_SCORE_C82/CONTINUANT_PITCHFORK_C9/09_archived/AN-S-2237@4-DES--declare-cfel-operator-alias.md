---
atom_family: SPEC
atom_id: AN-S-2237
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 4
  updated_at: "2026-11-25T22:57:06.750373+00:00"
---
## Summary

Declare CFEL operator alias

## Claim

### Prose Claim

`alias(Relation//RELATION_NAME) == "notation token"` takes a qualified canonical Relation model name or its declared inverse alias model name and binds that written name to one nonempty lexical notation token in the selected effective MODEL. Resolve the name exactly; do not infer case folding or undeclared synonyms. Each written name has at most one authored short token. Reject undeclared Relation names, conflicting alias values and ambiguous token bindings. Without an alias, use the full named Relation notation.

This CFEL operator binds notation metadata; an inverse alias name is not a separate Relation entity; it does not construct a literal-to-Node graph Relation or equate different Relation identities. The token follows its written name's directional reading and grants no endpoint permission, cardinality or second authored fact. In a graph expression, `Relation//NAME` references a canonical Relation model name or its declared inverse alias model name, whereas `((NAME))` invokes that Relation between endpoints.
### Formal Claim

```python
# model
set_value(address='Operator//Alias', value='"alias(Relation//RELATION_NAME) == \\"notation token\\""')
```

