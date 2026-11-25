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
  status: "active"
  version: 23
  updated_at: "2026-11-25T20:41:49.897113+00:00"
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

The Atom’s Header and Content are its source of truth. Header.Container determines its containment. Carry the applicable authored properties on the Atom. Resolve other Atoms and governing declarations by reference.

Each contained Atom has its own identity and lifecycle. A change confined to the contained Atoms preserves the containing Atom’s identity.

Derive the expected Carrier filename and path from the Header and Content Summary using the declared Project Structure. A different filename or path is a placement discrepancy.
