---
atom_family: SPEC
atom_id: AN-S-2134
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_node
state:
  status: "archived"
  version: 4
  updated_at: "2026-11-25T19:40:35.113904+00:00"
---

## Summary

Declare Projection

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Artifact//Derived//Projection

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Derived

class Projection(Derived):
    pass
```

## Semantics

A Projection is a derived view of source Atoms. It does not establish or override their Claims.
