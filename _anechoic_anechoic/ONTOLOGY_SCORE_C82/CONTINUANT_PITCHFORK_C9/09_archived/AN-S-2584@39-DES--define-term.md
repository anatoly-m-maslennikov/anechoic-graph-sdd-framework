---
atom_family: SPEC
atom_id: AN-S-2584
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: "archived"
  version: 39
  updated_at: "2026-11-25T23:14:21.144273+00:00"
---
## Summary

Define Term

## Claim

### Prose Claim

A Term is a reusable word or phrase component of entity expressions and authored content. Its Project-specific meaning remains consistent across uses and is owned by its active Method/Form Term Definition. Vocabulary Terms are lexical items, not graph Nodes merely because they are used as words. A Term has one Name.

Use the full admitted canonical expression when identifying or comparing an entity. Reusing a Term within distinct expressions neither makes those expressions synonymous nor establishes a Relation between their referents. Literal source quotations and code identifiers are not automatically renamed. A lexical Term and an Entity whose complete name uses that Term have distinct targets and meaning owners.

### Formal Claim

```python
from anechoic.formal_claims import declare_entity


class Term:
    name: str


declare_entity(entity_class=Term, entity_name="Term")
```

## Semantics

A Term provides a reusable word or phrase; its full context supplies the expression in which it appears.
