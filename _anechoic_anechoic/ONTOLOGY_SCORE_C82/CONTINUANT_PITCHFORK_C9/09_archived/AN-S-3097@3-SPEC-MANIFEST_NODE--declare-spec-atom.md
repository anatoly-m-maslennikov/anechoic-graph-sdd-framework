---
atom_family: SPEC
atom_id: AN-S-3097
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_node
state:
  status: "archived"
  version: 3
  updated_at: '2026-11-24T16:58:01.341194+00:00'
---

## Summary

Declare Spec Atom

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Artifact//SSOT//Prescribed/Content/Atom//Specification

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Atom

class SpecAtom(Atom):
    classifications = {'Temporal Kind': 'Continuant'}
```
