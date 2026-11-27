---
atom_family: SPEC
atom_id: AN-S-4841
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_node
state:
  status: "archived"
  version: 1
  updated_at: "2026-11-26T14:46:18.828125+00:00"
---

## Summary

Declare Prompt

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Artifact//SSOT//Realization/Content/Prompt

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Realization

class Prompt(Realization):
    pass
```
