---
atom_family: SPEC
atom_id: AN-S-3111
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_node
state:
  status: "archived"
  version: 5
  updated_at: "2026-11-25T22:32:16.797048+00:00"
---

## Summary

Declare Project Goal

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Artifact//SSOT//Prescribed/Content/Atom//Specification//Purpose//Project Goal

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Purpose

class ProjectGoal(Purpose):
    pass
```

## Semantics

A Project Goal states an intended outcome of the Project. A Project may have zero or more Active Project Goals.
