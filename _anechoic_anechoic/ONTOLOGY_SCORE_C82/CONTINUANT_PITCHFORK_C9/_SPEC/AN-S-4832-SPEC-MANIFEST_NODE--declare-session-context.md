---
atom_family: SPEC
atom_id: AN-S-4832
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_node
state:
  status: "active"
  version: 2
  updated_at: "2026-11-25T16:00:38.183555+00:00"
---

## Summary

Declare Session Context

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Ephemeral//Session Context

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Ephemeral

class SessionContext(Ephemeral):
    node.classifications = {'Artifact Kind': 'Ephemeral'}
```
