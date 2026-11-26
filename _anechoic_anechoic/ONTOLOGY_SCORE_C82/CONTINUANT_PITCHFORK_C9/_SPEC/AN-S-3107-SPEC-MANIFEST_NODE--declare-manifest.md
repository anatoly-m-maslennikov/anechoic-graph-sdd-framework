---
atom_family: SPEC
atom_id: AN-S-3107
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_node
state:
  status: "active"
  version: 3
  updated_at: '2026-11-24T16:58:01.363756+00:00'
---

## Summary

Declare Manifest

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Artifact//SSOT//Prescribed/Content/Atom//Specification//Manifest

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import SpecAtom

class Manifest(SpecAtom):
    pass
```
