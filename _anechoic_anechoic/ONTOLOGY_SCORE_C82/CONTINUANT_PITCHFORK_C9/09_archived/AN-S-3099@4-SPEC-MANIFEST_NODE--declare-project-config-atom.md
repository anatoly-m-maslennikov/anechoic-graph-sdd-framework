---
atom_family: SPEC
atom_id: AN-S-3099
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_node
state:
  status: "archived"
  version: 4
  updated_at: "2026-11-26T15:54:02.069938+00:00"
---

## Summary

Declare Project Config Atom

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Artifact//SSOT//Prescribed/Content/Atom//project_config

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Atom

class ProjectConfigAtom(Atom):
    node.classifications = {'Temporal Kind': 'Continuant'}
```
