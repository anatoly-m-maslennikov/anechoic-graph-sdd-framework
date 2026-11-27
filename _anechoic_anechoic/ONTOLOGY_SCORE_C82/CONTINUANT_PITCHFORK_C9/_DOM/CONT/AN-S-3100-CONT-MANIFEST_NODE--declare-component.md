---
atom_family: SPEC
atom_id: AN-S-3100
concern:
  subject: Component
  path: Model/Graph/Node//Artifact//SSOT//Prescribed/Structure
  relation: is_contained_by
container:
  component: C9
tier: 2
context:
  template: manifest_node
  lens: DOM/CONT
state:
  status: "active"
  version: 7
  updated_at: "2026-11-26T14:46:18.768127+00:00"
---

## Summary

Declare Component

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.formal_claims import value
from anechoic.model import MarkdownWithYAMLFrontMatter, Prescribed

class Component(Prescribed):
    node.ssot_carrier = value(fixed=MarkdownWithYAMLFrontMatter)
```

## Semantics

A Component groups its owned Spec Atoms within a responsibility boundary. Its declared hierarchy also governs the corresponding Component Packages. The authoritative source is the Formal Manifest section of its Active Component Manifest. The root Component uses the Project Manifest.

A folder that represents a child Component ends in an underscore followed by the Component’s stable ID.
