---
atom_family: SPEC
atom_id: AN-S-4836
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_node
state:
  status: "archived"
  version: 2
  updated_at: "2026-11-26T15:54:02.939385+00:00"
---

## Summary

Declare Atom Companion Container

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Artifact//SSOT//Prescribed/Structure/Atom Companion Container

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Prescribed

class AtomCompanionContainer(Prescribed):
    pass
```

## Semantics

The companion folder sits beside its owning Atom’s Carrier. Its name is the Atom’s full filename without `.md`. The folder provides the location for the Atom’s children.
