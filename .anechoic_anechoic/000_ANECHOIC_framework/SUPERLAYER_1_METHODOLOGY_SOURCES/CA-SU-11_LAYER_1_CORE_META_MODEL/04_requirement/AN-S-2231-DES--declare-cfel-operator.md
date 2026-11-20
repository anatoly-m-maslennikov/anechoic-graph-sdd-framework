---
identity:
  atom_id: AN-S-2231
context:
  container:
    component: C9
  tier: 3
  lens: DES
state:
  status: active
  version: 3
  updated_at: '2026-11-13T05:35:36.099791+00:00'
---
## Summary

Declare CFEL Operator

## Claim

### Prose Claim


A CFEL Operator is one declared language component with one token or bounded construct meaning. Each individual operator-instance Declaration supplies its own token semantics. A CFEL Operator is distinct from a graph Relation and does not create a Node, Relation fact, Property occurrence, Carrier fact, or runtime operation. Its declared operator descriptor may be a graph endpoint where a Relation signature admits declared model entities; a glyph or literal operand is not another model entity.


### Formal Claim

```python
# model
composition(container="CFEL", parts=("Operator",))
```

## Semantics

CFEL<+Operator//Name identifies a declared CFEL operator by semantic name.
Graph Relations and their canonical, derived, inverse, and counterpart semantics
remain in Relation Declarations; punctuation alone does not admit a counterpart.
