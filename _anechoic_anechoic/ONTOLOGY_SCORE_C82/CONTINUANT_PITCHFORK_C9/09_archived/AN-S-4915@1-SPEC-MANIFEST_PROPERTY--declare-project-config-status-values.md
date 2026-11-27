---
atom_family: SPEC
atom_id: AN-S-4915
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_property
state:
  status: "archived"
  version: 1
  updated_at: "2026-11-26T15:54:03.504028+00:00"
---

## Summary

Declare Project Config Status values

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Artifact//SSOT//Prescribed/Content/Atom//project_config.Header.State.Status

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Atom, Property, ProjectConfigAtom

class ProjectConfigAtomStatus(Property):
    name = 'Status'
    bearer = Atom.Header.State
    property.applies_to = (ProjectConfigAtom,)
    property.value.allowed = ('draft', 'active', 'archived')
```
