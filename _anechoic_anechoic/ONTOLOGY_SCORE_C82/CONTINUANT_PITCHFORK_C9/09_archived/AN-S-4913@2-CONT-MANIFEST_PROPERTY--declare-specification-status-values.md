---
atom_family: SPEC
atom_id: AN-S-4913
concern:
  subject: Status
  path: Model/Graph/Node//Artifact//SSOT//Prescribed/Content/Atom//Specification.Header.State
  relation: is_property_of
container:
  component: C9
tier: 2
context:
  template: manifest_property
  lens: DOM/CONT
state:
  status: archived
  version: 2
  updated_at: '2026-11-28T09:09:18.233112+00:00'
---

## Summary

Declare Specification Status values

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Atom, Property, SpecAtom

class SpecAtomStatus(Property):
    name = 'Status'
    bearer = Atom.Header.State
    property.applies_to = (SpecAtom,)
    property.value.allowed = ('draft', 'ready', 'active', 'archived')
```
