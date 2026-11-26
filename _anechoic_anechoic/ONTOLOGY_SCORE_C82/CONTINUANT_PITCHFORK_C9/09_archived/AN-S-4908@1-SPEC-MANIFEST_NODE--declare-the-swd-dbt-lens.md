---
atom_family: SPEC
atom_id: AN-S-4908
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_node
state:
  status: "archived"
  version: 1
  updated_at: "2026-11-25T12:40:53.739076+00:00"
relations:
  IS_REFERENCE:
  - AN-T-3922@1
---

## Summary

Declare the SWD/DBT Lens

## Semantics

Groups dbt-style rules for the roles, dependencies, and refresh of the Project’s data transformations.

## Claim scope

MODEL//ANECHOIC <+ Graph/Lens/Software Development Lens/Data Build Tool Lens

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.formal_claims import value
from anechoic.model import Lens

class DataBuildToolLens(Lens):
    lens_path = value(fixed='SWD/DBT')
```
