---
atom_family: SPEC
atom_id: AN-S-2125
concern:
  subject: Status
  path: Model/Graph/Node//Artifact//SSOT//Prescribed/Content/Atom.Header.State
  relation: is_property_of
container:
  component: C9
tier: 2
context:
  template: manifest_property
  lens: DOM/CONT
state:
  status: archived
  version: 12
  updated_at: '2026-11-28T09:59:20.838906+00:00'
---
## Summary

Declare Atom.Status

## Semantics

Status records an Atom revision's lifecycle state. The base Property
supplies the Current, Draft, and Archived groups. A family refinement
supplies its allowed Status values and their group membership.

A Project Config Custom Model Property can add Current Ticket statuses.
Use the same bearer, Concern, and Ticket scope as the base declaration.
List the new values in `property.value.allowed`. The Model retains the
base values and puts Project-added values in Current. It reserves
Draft, Ready, Active, Archived, and In Progress.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Atom, Property

class Property2125(Property):
    name = 'Status'
    bearer = Atom.Header.State
    field_options = {'kw_only': True}
    property.cardinality = 1
    property.value.cardinality = 1
    property.value.format = str
    property.value.group_names = ('Current', 'Draft', 'Archived')
```
