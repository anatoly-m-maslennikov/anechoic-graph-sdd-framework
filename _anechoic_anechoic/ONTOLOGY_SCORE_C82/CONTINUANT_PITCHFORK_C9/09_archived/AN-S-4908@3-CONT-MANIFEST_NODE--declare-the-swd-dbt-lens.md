---
atom_family: SPEC
atom_id: AN-S-4908
concern:
  subject: Data Build Tool Lens
  path: Model/Graph/Lens/Software Development Lens
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
  updated_at: "2026-11-26T18:00:26.217300+00:00"
---

## Summary

Declare the SWD/DBT Lens

## Semantics

Groups dbt-style rules for the roles, dependencies, and refresh of the Project’s data transformations.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.formal_claims import value
from anechoic.model import Lens

class DataBuildToolLens(Lens):
    node.lens_path = value(fixed='SWD/DBT')
```
