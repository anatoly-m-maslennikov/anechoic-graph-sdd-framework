---
atom_family: SPEC
atom_id: AN-S-4901
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_node
state:
  status: "active"
  version: 2
  updated_at: "2026-11-25T16:00:38.313645+00:00"

---

## Summary

Declare the DOM Lens

## Semantics

Groups the definitions and methods for a Domain through its Ontology and Methodology sublenses.

## Claim scope

MODEL//ANECHOIC <+ Graph/Lens/Domain Lens

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.formal_claims import value
from anechoic.model import Lens

class DomainLens(Lens):
    node.lens_path = value(fixed='DOM')
```
