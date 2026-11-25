---
atom_family: SPEC
atom_id: AN-S-3155
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_node
state:
  status: "archived"
  version: 3
  updated_at: '2026-11-24T16:58:01.456400+00:00'
---

## Summary

Declare Component Seed Manifest Constraints

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Artifact//SSOT//Prescribed/Content/Atom//Specification//Manifest//Component Seed Manifest.Constraints

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Component, ComponentSeedManifest, NodeConstraints

def check_component_seed_manifest(spec: ComponentSeedManifest) -> bool:
    return bool(spec.component_seed_id.startswith("CS") and spec.component_seed_id[2:].isascii()
                and spec.component_seed_id[2:].isdigit() and spec.purpose.strip() and spec.solution.strip())

class Constraints(NodeConstraints):
    bearer = ComponentSeedManifest
    instance_check = check_component_seed_manifest
    instance_relation_constraints = {'CONTAINED_BY': {'target_entity_paths': (Component,), 'targets_per_source': 1}}
```
