---
atom_family: SPEC
atom_id: AN-S-4902
concern:
  subject: Ontology Lens
  path: Model/Graph/Lens/Domain Lens
  relation: is_contained_by
container:
  component: C9
tier: 2
context:
  template: manifest_node
  lens: DOM/CONT
state:
  status: "archived"
  version: 3
  updated_at: "2026-11-26T18:00:26.237646+00:00"
---

## Summary

Declare the DOM/ONT Lens

## Semantics

Defines the kinds of entities in a Domain, their relationships, and the rules that hold for them.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.formal_claims import value
from anechoic.model import Lens

class OntologyLens(Lens):
    node.lens_path = value(fixed='DOM/ONT')
    node.control_flow = value(fixed='Declarative')
```
