---
atom_family: SPEC
atom_id: AN-S-3155
concern:
  subject: Constraints
  path: Model/Graph/Node//Artifact//SSOT//Prescribed/Content/Atom//Specification//Manifest//Component Seed Manifest
  relation: is_property_of
container:
  component: C9
tier: 2
context:
  template: manifest_node
  lens: DOM/CONT
state:
  status: archived
  version: 7
  updated_at: "2026-11-26T15:52:33.356004+00:00"
---

## Summary

Declare Component Seed Manifest Constraints

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Component, ComponentSeedManifest, NodeConstraints

def check_component_seed_manifest(spec: ComponentSeedManifest) -> bool:
    return bool(spec.component_seed_id.startswith("CS") and spec.component_seed_id[2:].isascii()
                and spec.component_seed_id[2:].isdigit())

class Constraints(NodeConstraints):
    bearer = ComponentSeedManifest
    node.constraints.instance_check = check_component_seed_manifest
    node.constraints.instance_relations = {'IS_CONTAINED_BY': {'target_entity_paths': (Component,), 'targets_per_source': 1}}
```
