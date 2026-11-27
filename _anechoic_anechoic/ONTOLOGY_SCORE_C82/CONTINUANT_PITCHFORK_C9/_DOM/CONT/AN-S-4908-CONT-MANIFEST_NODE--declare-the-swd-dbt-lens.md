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
  status: active
  version: 5
  updated_at: '2026-11-26T18:18:17.060286+00:00'
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

## Sources

- [ISO/IEC 9075-2:2023 — SQL/Foundation](https://www.iso.org/standard/76584.html)
- [dbt project structure guide](https://docs.getdbt.com/best-practices/how-we-structure/1-guide-overview) explains transformation layers.
