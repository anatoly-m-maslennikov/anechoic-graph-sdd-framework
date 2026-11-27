---
atom_family: SPEC
atom_id: AN-S-4835
concern:
  subject: Atom Family
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
  version: 2
  updated_at: "2026-11-26T14:46:18.813698+00:00"
---

## Summary

Declare Atom Family

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.formal_claims import value
from anechoic.model import MarkdownWithYAMLFrontMatter, Prescribed

class AtomFamily(Prescribed):
    node.ssot_carrier = value(fixed=MarkdownWithYAMLFrontMatter)
```

## Semantics

The family’s formal declaration carries its definition.
