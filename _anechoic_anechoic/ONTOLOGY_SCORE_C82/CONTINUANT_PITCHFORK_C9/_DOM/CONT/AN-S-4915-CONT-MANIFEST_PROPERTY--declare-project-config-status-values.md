---
atom_family: SPEC
atom_id: AN-S-4915
concern:
  subject: Status
  path: Model/Graph/Node//Artifact//SSOT//Prescribed/Content/Atom//project_config.Header.State
  relation: is_property_of
container:
  component: C9
tier: 2
context:
  template: manifest_property
  lens: DOM/CONT
state:
  status: "active"
  version: 2
  updated_at: "2026-11-26T15:52:36.974169+00:00"
---

## Summary

Declare Project Config Status values

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
