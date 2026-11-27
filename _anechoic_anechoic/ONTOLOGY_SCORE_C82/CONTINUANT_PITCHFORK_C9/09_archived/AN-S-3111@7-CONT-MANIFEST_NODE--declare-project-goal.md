---
atom_family: SPEC
atom_id: AN-S-3111
concern:
  subject: Project Goal
  path: Model/Graph/Node//Artifact//SSOT//Prescribed/Content/Atom//Specification//Purpose
  relation: is_narrower_than
container:
  component: C9
tier: 2
context:
  template: manifest_node
  lens: DOM/CONT
state:
  status: "archived"
  version: 7
  updated_at: "2026-11-26T17:13:49.060699+00:00"
---

## Summary

Declare Project Goal

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Purpose

class ProjectGoal(Purpose):
    pass
```

## Semantics

A Project Goal states an intended outcome of the Project. A Project may have zero or more Active Project Goals. Project Goals express outcomes. Component Manifests govern Component Structure.
