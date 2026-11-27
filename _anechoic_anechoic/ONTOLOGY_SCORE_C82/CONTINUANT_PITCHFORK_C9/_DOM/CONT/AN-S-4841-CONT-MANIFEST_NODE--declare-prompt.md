---
atom_family: SPEC
atom_id: AN-S-4841
concern:
  subject: Prompt
  path: Model/Graph/Node//Artifact//SSOT//Realization/Content
  relation: is_contained_by
container:
  component: C9
tier: 2
context:
  template: manifest_node
  lens: DOM/CONT
state:
  status: "active"
  version: 2
  updated_at: "2026-11-26T14:46:18.832507+00:00"
---

## Summary

Declare Prompt

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.formal_claims import value
from anechoic.model import File, Realization

class Prompt(Realization):
    node.ssot_carrier = value(fixed=File)
```

## Semantics

The source file stores the authored Prompt.
