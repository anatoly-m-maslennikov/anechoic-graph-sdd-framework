---
atom_family: SPEC
atom_id: AN-S-3108
concern:
  subject: Project Manifest
  path: Model/Graph/Node//Artifact//SSOT//Prescribed/Content/Atom//Specification//Manifest
  relation: is_narrower_than
container:
  component: C9
tier: 2
context:
  template: manifest_node
  lens: DOM/CONT
state:
  status: "archived"
  version: 5
  updated_at: "2026-11-26T17:13:49.037876+00:00"
---

## Summary

Declare Project Manifest

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Manifest

class ProjectManifest(Manifest):
    pass
```
