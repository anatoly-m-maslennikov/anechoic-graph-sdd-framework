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
  version: 5
  updated_at: "2026-11-25T22:54:35.281115+00:00"
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

## Semantics

An SSOT Artifact is the authoritative source for the facts it carries. Each fact has one authoritative source within its applicable context. A derived representation preserves that source binding.
