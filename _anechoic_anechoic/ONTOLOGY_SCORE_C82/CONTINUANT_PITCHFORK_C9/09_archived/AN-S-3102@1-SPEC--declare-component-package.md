---
atom_family: SPEC
atom_id: AN-S-3102
container:
  component: C9
tier: 2
context:
  lens: SPEC
state:
  status: archived
  version: 1
  updated_at: '2026-11-20T11:17:59+00:00'
---

## Summary

Declare Component Package

## Claim scope

MODEL//ANECHOIC <+ Node//Artifact//Package//Component Package

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Package

class ComponentPackage(Package):
    pass

declare_entity(entity_name="Component Package", entity_class=ComponentPackage)
```
