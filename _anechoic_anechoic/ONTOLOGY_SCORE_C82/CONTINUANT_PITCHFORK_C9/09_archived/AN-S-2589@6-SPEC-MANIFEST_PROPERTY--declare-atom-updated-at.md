---
atom_family: SPEC
atom_id: AN-S-2589
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_property
state:
  status: "archived"
  version: 6
  updated_at: '2026-11-24T16:58:01.309668+00:00'
---
## Summary

Declare Atom.Updated At

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Artifact//SSOT//Prescribed/Content/Atom.Header.State.Updated At

## Claim

### Prose Claim

The Updated At value equals the maximum happened_at among Event Records whose single object_output has a version, has this Atom ID and current Version, and has action create or update.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Atom, Property
from datetime import datetime

class Property2589(Property):
    name = 'Updated At'
    bearer = Atom.Header.State
    field_options = {'kw_only': True}
    property_occurrence_cardinality = 1
    value_cardinality = 1
    value_format = datetime
```
