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
  status: archived
  version: 3
  updated_at: "2026-11-28T10:14:16.621462+00:00"
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
    property.value.groups = {'draft': 'Draft', 'active': 'Current', 'archived': 'Archived'}
```
