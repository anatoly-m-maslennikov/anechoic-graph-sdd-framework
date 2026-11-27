---
atom_family: SPEC
atom_id: AN-S-4913
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_property
state:
  status: "archived"
  version: 1
  updated_at: "2026-11-26T15:54:03.476294+00:00"
---

## Summary

Declare Specification Status values

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Artifact//SSOT//Prescribed/Content/Atom//Specification.Header.State.Status

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
