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
  status: "archived"
  version: 1
  updated_at: "2026-11-25T12:40:53.287271+00:00"
relations:
  IS_REFERENCE:
  - AN-T-3922@1
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
    lens_path = value(fixed='DOM')
```
