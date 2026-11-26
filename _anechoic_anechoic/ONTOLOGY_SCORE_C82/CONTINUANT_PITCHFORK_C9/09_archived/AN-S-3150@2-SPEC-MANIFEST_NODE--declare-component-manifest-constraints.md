---
atom_family: SPEC
atom_id: AN-S-3150
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_node
state:
  status: "archived"
  version: 2
  updated_at: '2026-11-24T16:58:01.446398+00:00'
---

## Summary

Declare Component Manifest Constraints

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Artifact//SSOT//Prescribed/Content/Atom//Specification//Manifest//Component Manifest.Constraints

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Component, ComponentManifest, NodeConstraints

def check_component_manifest(manifest: ComponentManifest) -> bool:
    return bool(manifest.component_id.strip() and manifest.name.strip())

class Constraints(NodeConstraints):
    bearer = ComponentManifest
    instance_check = check_component_manifest
    instance_relation_constraints = {'CONTAINED_BY': {'target_entity_paths': (Component,), 'targets_per_source': 1}}
```
