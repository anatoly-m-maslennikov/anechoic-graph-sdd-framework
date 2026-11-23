---
atom_family: SPEC
atom_id: AN-S-2584
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 38
  updated_at: '2026-11-13T05:35:59.629049+00:00'
---
## Summary

Define Term

## Claim

### Prose Claim

A Term is a reusable word or phrase component of entity expressions and authored content. Its Project-specific meaning remains consistent across uses and is owned by its active Method/Form Term Definition. Vocabulary Terms are lexical items, not graph Nodes merely because they are used as words. A Term has one Name.

Use the full admitted canonical expression when identifying or comparing an entity. Reusing a Term within distinct expressions neither makes those expressions synonymous nor establishes a Relation between their referents. Literal source quotations and code identifiers are not automatically renamed. A lexical Term and an Entity whose complete name uses that Term have distinct targets and meaning owners.

### Formal Claim

```python
# model
allowed_children(address='Term', names=('Name',), occurrences='1')
relation(source='Term.**', source_count='1', name='IS_PROPERTY_OF', target='(Term, Term.**)')
relation(source='(Term, Term.**)', source_count='0+', name='HAS_PROPERTY', target='Term.**')
# instances
subject_path(address='Term//$term')
relation(source='$term.**', source_count='1', name='IS_PROPERTY_OF', target='($term, $term.**)')
relation(source='($term, $term.**)', source_count='0+', name='HAS_PROPERTY', target='$term.**')
```

## Semantics

A Term provides a reusable word or phrase; its full context supplies the expression in which it appears.
