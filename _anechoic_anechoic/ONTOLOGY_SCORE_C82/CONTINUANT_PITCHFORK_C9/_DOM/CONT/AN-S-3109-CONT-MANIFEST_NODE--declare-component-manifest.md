---
atom_family: SPEC
atom_id: AN-S-3109
concern:
  path: Model/Graph/Node//Artifact//SSOT//Prescribed/Content/Atom//Specification//Manifest//.Header.Context
  relation: .
  subject: Template := component_manifest
container:
  component: C9
tier: 2
context:
  template: manifest_node
  lens: DOM/CONT
state:
  status: active
  version: 8
  updated_at: '2026-11-26T17:41:09.832474+00:00'
---

## Summary

Declare Component Manifest

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.formal_claims import value
from anechoic.model import Manifest

class ComponentManifest(Manifest):
    node.template = value(fixed='component_manifest')
```
