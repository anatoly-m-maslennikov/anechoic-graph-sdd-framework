---
atom_family: SPEC
atom_id: AN-S-4836
concern:
  subject: Atom Companion Container
  path: Model/Graph/Node//Artifact//SSOT//Prescribed/Structure
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
  updated_at: "2026-11-26T17:13:49.240074+00:00"
---

## Summary

Declare Atom Companion Container

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Prescribed

class AtomCompanionContainer(Prescribed):
    pass
```

## Semantics

The companion folder sits beside its owning Atom’s Carrier. Its name is the Atom’s full filename without `.md`. The folder represents the containment declared by the child Atom Headers.
