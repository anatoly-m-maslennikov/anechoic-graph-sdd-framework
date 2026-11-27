---
atom_family: SPEC
atom_id: AN-S-4900
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_node
state:
  status: "archived"
  version: 2
  updated_at: "2026-11-26T15:54:03.276563+00:00"

---

## Summary

Declare the DES/DOM Lens

## Semantics

Groups domain workflows, actions, and steps specified as part of a design.

## Claim scope

MODEL//ANECHOIC <+ Graph/Lens/Design Lens/Design Domain Lens

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.formal_claims import value
from anechoic.model import Lens

class DesignDomainLens(Lens):
    node.lens_path = value(fixed='DES/DOM')
```
