---
atom_family: SPEC
atom_id: AN-S-3198
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_node
state:
  status: "archived"
  version: 2
  updated_at: '2026-11-24T16:58:01.506709+00:00'
---

## Summary

Declare Applicable Principle Constraints

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Artifact//SSOT//Prescribed/Content/Atom//Specification//Applicable Principle.Constraints

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import ApplicablePrinciple, NodeConstraints, Project

class Constraints(NodeConstraints):
    bearer = ApplicablePrinciple
    instance_relation_constraints = {'CONTAINED_BY': {'target_entity_paths': (Project,), 'targets_per_source': 1}}
```
