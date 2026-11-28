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
  status: active
  version: 13
  updated_at: "2026-11-28T11:00:50.522707+00:00"
---
## Summary

Declare Atom.Status

## Semantics

Status records an Atom revision's lifecycle state. The base Property
defines Current, Draft, and Archived. Every family inherits `draft` in
Draft and `archived` in Archived. A family declares only its additional
Status memberships. The effective membership map supplies the allowed values.

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
    property.value.groups = {'draft': 'Draft', 'archived': 'Archived'}
```
