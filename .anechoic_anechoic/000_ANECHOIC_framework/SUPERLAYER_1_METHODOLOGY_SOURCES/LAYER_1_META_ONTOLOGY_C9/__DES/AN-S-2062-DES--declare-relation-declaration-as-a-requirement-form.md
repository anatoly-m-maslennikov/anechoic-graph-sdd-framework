---
atom_family: SPEC
atom_id: AN-S-2062
structure:
  container:
    component: C9
  tier: 3
context:
  lens: DES
state:
  status: active
  version: 3
  updated_at: '2026-11-12T17:23:54+00:00'
---

## Summary

Declare Relation Declaration as a Requirement Form

## Claim

### Prose Claim

This Form uses the Declaration contract.

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Requirement

class RelationDeclaration(Requirement):
    pass

declare_entity(entity_class=RelationDeclaration, entity_name='Relation Declaration', qualification_property_path="Atom.Header.Context.Form")
```

## Semantics

A Relation Declaration defines a canonical binary Relation, its endpoint domains and applicable inverse aliases.
