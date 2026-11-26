---
atom_family: SPEC
atom_id: AN-S-4831
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_node
state:
  status: "active"
  version: 2
  updated_at: "2026-11-25T16:00:38.180001+00:00"
---

## Summary

Declare Derived

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Artifact//Derived

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Artifact

class Derived(Artifact):
    node.classifications = {'Artifact Kind': 'Artifact'}
```
