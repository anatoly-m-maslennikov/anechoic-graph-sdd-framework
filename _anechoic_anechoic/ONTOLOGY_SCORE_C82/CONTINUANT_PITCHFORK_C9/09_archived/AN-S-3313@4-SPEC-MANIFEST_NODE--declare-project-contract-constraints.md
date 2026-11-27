---
atom_family: SPEC
atom_id: AN-S-3313
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_node
state:
  status: "archived"
  version: 4
  updated_at: "2026-11-26T15:54:02.672181+00:00"
---

## Summary

Declare Project Contract Constraints

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Artifact//SSOT//Prescribed/Content/Atom//Specification//Contract//Project Contract.Constraints

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import NodeConstraints, Project, ProjectContract

class Constraints(NodeConstraints):
    bearer = ProjectContract
    node.constraints.instance_relations = {'IS_CONTAINED_BY': {'target_entity_paths': (Project,), 'targets_per_source': 1}}
```
