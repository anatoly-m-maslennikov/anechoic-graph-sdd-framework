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
  status: "active"
  version: 4
  updated_at: "2026-11-25T16:00:37.761674+00:00"
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
    node.classifications = {'Artifact Kind': 'Artifact'}
```
