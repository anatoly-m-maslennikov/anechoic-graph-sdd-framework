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
  version: 7
  updated_at: "2026-11-25T19:30:50.391988+00:00"
---
## Summary

Declare Atom.Updated At

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
    property.cardinality = 1
    property.value.cardinality = 1
    property.value.format = datetime
```
