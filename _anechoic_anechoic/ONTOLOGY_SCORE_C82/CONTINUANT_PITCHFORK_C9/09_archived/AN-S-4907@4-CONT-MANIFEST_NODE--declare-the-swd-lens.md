---
atom_family: SPEC
atom_id: AN-S-4907
concern:
  subject: SWD
  path: Model/Graph/Lens//SPEC//SWE
  relation: is_narrower_than
container:
  component: C9
tier: 2
context:
  template: manifest_node
  lens: DOM/CONT
state:
  status: "archived"
  version: 4
  updated_at: "2026-11-26T18:18:20.904798+00:00"
---

## Summary

Declare the SWD Lens

## Semantics

Groups engineering rules for implementing and maintaining software.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.formal_claims import value
from anechoic.model import SoftwareEngineeringLens, DataBuildToolLens

class SoftwareDevelopmentLens(SoftwareEngineeringLens):
    node.lens_path = value(fixed='SWD')
    node.parts = {
        'DBT': DataBuildToolLens,
    }
```
