---
atom_family: SPEC
atom_id: AN-S-2715
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: draft
  version: 6
  updated_at: 2026-11-05 18:23:39 +0400
---
## Summary

Define composition and its inverse

## Claim

### Prose Claim

The Target has classification `Container = yes`.

### Formal Claim

```python
# model
relation(source='$part', name='IS_CONTAINED_BY', target='$container')
relation(source='Relation//CONTAINS', name='IS_INVERSE_ALIAS_FOR', target='Relation//IS_CONTAINED_BY')
set_value(address='alias(Relation//IS_CONTAINED_BY)', value='"+>"')
set_value(address='alias(Relation//CONTAINS)', value='"/"')
classify(address='Relation//IS_CONTAINED_BY', axis='Derivation', value='Direct', notation='relation')
```

## Semantics

IS_CONTAINED_BY relates a declared Entity or instance to its immediate Container. CONTAINS is its inverse alias; both writings identify the same fact. `Whole/Part` writes the inverse view and `Part +> Whole` the canonical direction. Containment does not imply narrowing or inheritance.
