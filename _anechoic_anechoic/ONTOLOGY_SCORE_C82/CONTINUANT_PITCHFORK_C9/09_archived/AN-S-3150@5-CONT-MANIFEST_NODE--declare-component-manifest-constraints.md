---
atom_family: SPEC
atom_id: AN-S-3150
concern:
  subject: Constraints
  path: Model/Graph/Node//Artifact//SSOT//Prescribed/Content/Atom//Specification//Manifest//Component Manifest
  relation: is_property_of
container:
  component: C9
tier: 2
context:
  template: manifest_node
  lens: DOM/CONT
state:
  status: archived
  version: 5
  updated_at: "2026-11-26T15:52:33.180823+00:00"
---

## Summary

Declare Component Manifest Constraints

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Component, ComponentManifest, NodeConstraints

def check_component_manifest(manifest: ComponentManifest) -> bool:
    return bool(manifest.component_id.strip() and manifest.name.strip())

class Constraints(NodeConstraints):
    bearer = ComponentManifest
    node.constraints.instance_check = check_component_manifest
    node.constraints.instance_relations = {'IS_CONTAINED_BY': {'target_entity_paths': (Component,), 'targets_per_source': 1}}
```
