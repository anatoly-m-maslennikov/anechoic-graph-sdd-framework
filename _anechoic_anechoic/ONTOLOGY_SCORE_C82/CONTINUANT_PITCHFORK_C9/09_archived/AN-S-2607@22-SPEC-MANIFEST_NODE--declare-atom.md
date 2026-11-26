---
atom_family: SPEC
atom_id: AN-S-2607
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_node
state:
  status: "archived"
  version: 22
  updated_at: "2026-11-25T20:41:49.831073+00:00"
---

## Summary

Declare Atom

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Artifact//SSOT//Prescribed/Content/Atom

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Prescribed

class Atom(Prescribed):
    node.identity = header.atom_id
```

## Semantics

The Atom’s Header and Content are its source of truth. Header.Container determines its containment.

Derive the expected Carrier filename and path from the Header and Content Summary using the declared Project Structure. A different filename or path is a placement discrepancy.
