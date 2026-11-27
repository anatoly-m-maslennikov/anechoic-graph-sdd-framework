---
atom_family: SPEC
atom_id: AN-S-4833
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_node
state:
  status: "archived"
  version: 2
  updated_at: "2026-11-26T15:54:02.908450+00:00"
---

## Summary

Declare Session Task

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Ephemeral//Session Task

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Ephemeral

class SessionTask(Ephemeral):
    node.classifications = {'Artifact Kind': 'Ephemeral'}
```
