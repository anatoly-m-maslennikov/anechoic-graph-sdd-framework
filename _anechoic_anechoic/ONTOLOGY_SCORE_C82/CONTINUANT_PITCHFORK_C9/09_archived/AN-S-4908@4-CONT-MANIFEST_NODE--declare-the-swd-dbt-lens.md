---
atom_family: SPEC
atom_id: AN-S-4908
concern:
  subject: DBT
  path: Model/Graph/Lens//SPEC//SWE//SWD
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
  updated_at: "2026-11-26T18:18:20.912334+00:00"
---

## Summary

Declare the SWD/DBT Lens

## Semantics

Groups dbt-style rules for the roles, dependencies, and refresh of the Project’s data transformations.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.formal_claims import value
from anechoic.model import SoftwareDevelopmentLens

class DataBuildToolLens(SoftwareDevelopmentLens):
    node.lens_path = value(fixed='SWD/DBT')
```
