---
atom_family: SPEC
atom_id: AN-S-3105
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_node
state:
  status: "archived"
  version: 3
  updated_at: '2026-11-24T16:58:01.359070+00:00'
---

## Summary

Declare SSOT

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Artifact//SSOT

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Artifact

class SSOT(Artifact):
    classifications = {'Artifact Kind': 'Artifact'}
```
