---
atom_family: SPEC
atom_id: AN-S-3099
concern:
  subject: project_config
  path: Model/Graph/Node//Artifact//SSOT//Prescribed/Content/Atom
  relation: is_narrower_than
container:
  component: C9
tier: 2
context:
  template: manifest_node
  lens: DOM/CONT
state:
  status: "archived"
  version: 6
  updated_at: "2026-11-26T18:39:02.265249+00:00"
---

## Summary

Declare Project Config Atom

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Atom

class ProjectConfigAtom(Atom):
    node.axes = {'Temporal Kind': 'Continuant'}
```
