---
atom_family: SPEC
atom_id: AN-S-4902
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_node
state:
  status: "archived"
  version: 1
  updated_at: "2026-11-25T12:40:53.307769+00:00"
relations:
  IS_REFERENCE:
  - AN-T-3922@1
---

## Summary

Declare the DOM/ONT Lens

## Semantics

Defines the kinds of entities in a Domain, their relationships, and the rules that hold for them.

## Claim scope

MODEL//ANECHOIC <+ Graph/Lens/Domain Lens/Ontology Lens

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.formal_claims import value
from anechoic.model import Lens

class OntologyLens(Lens):
    lens_path = value(fixed='DOM/ONT')
    control_flow = value(fixed='Declarative')
```
