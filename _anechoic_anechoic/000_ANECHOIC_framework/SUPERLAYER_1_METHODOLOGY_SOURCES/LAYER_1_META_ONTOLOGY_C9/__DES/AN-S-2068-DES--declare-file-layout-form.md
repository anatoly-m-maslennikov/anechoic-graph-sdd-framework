---
atom_family: SPEC
atom_id: AN-S-2068
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: active
  version: 2
  updated_at: '2026-11-12T17:23:54+00:00'
---

## Summary

Declare File Layout Form

## Claim

### Prose Claim

A File Layout Claim specifies how delivered files are named, where they are placed, or how files and folders are arranged. Paths are relative to the repository root.

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Delivery

class FileLayout(Delivery):
    pass

declare_entity(entity_class=FileLayout, entity_name='File Layout', qualification_property_path="Atom.Header.Context.Form")
```
