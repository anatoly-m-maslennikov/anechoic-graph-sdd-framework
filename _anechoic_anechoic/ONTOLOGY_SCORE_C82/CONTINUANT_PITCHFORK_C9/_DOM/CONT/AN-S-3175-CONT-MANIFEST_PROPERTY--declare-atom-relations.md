---
atom_family: SPEC
atom_id: AN-S-3175
concern:
  subject: Relations
  path: Model/Graph/Node//Artifact//SSOT//Prescribed/Content/Atom.Header
  relation: is_property_of
container:
  component: C9
tier: 2
context:
  template: manifest_property
  lens: DOM/CONT
state:
  status: "active"
  version: 8
  updated_at: "2026-11-26T15:52:33.813084+00:00"
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

A Relation states how this Atom is connected to another Atom. Different Relation names can express different facts about the same pair. Author each fact at its source. Derived inverse facts belong to the graph projection. Target order carries no Relation meaning. Use stable Atom IDs by default and exact revision references for History and Trace. A replacement identifies the earlier Atom whose contribution this Atom supersedes.
