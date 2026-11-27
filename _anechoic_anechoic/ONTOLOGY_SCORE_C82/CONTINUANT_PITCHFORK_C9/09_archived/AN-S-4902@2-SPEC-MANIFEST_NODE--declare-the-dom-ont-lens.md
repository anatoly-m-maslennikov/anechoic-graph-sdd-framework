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
  version: 2
  updated_at: "2026-11-26T15:54:03.330917+00:00"

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
    node.lens_path = value(fixed='DOM/ONT')
    node.control_flow = value(fixed='Declarative')
```
