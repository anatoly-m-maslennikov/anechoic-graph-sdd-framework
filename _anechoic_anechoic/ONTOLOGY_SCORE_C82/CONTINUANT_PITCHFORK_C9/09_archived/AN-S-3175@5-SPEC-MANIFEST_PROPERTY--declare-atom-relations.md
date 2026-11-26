---
atom_family: SPEC
atom_id: AN-S-3175
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_property
state:
  status: "archived"
  version: 5
  updated_at: "2026-11-25T20:09:41.944127+00:00"
---

## Summary

Declare Atom Relations

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Atom, Property, Relation
from anechoic.formal_claims import Cardinality

class atom_relations(Property):
    name = 'Relations'
    bearer = Atom.Header
    property.cardinality = Cardinality(minimum=0, maximum=1)
    property.value.cardinality = 0
    property.dependent_property.name.allowed = Relation.subclasses().name
    property.dependent_property.cardinality = Cardinality(minimum=1, maximum=None)
    property.dependent_property.value.cardinality = Cardinality(minimum=1, maximum=None)
    property.dependent_property.value.format = Relation.target_references()
    field_options = {'default': None, 'kw_only': True}
```

## Semantics

A Relation states how this Atom is connected to another Atom. Different Relation names can express different facts about the same pair. Author each fact at its source. Use stable Atom IDs by default and exact revision references for History and Trace. A replacement identifies the earlier Atom whose contribution this Atom supersedes.
