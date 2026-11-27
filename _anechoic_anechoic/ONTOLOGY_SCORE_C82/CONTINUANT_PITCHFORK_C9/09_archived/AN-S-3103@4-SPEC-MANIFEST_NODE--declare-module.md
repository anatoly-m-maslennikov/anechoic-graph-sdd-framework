---
atom_family: SPEC
atom_id: AN-S-3103
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_node
state:
  status: "archived"
  version: 4
  updated_at: "2026-11-26T14:46:18.772358+00:00"
---

## Summary

Declare Module

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Artifact//SSOT//Realization/Content/Module

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Realization

class Module(Realization):
    pass
```

## Claim

Each Module belongs to one Package. A Module directly in the realization root belongs to the Project Realization.
