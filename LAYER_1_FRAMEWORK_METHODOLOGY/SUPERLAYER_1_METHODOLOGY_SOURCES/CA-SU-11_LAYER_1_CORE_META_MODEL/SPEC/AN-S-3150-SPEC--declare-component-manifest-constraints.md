---
identity:
  atom_id: AN-S-3150
context:
  container:
    component: C9
  lens: SPEC
state:
  status: active
  version: 1
  updated_at: '2026-11-20T14:42:07.157939+00:00'
---

## Summary

Declare Component Manifest Constraints

## Claim scope

MODEL//ANECHOIC <+ Node//Artifact//Atom//Spec Atom//Manifest//Component Manifest.Constraints

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

def check_component_manifest(manifest: ComponentManifest) -> bool:
    return bool(manifest.component_id.strip() and manifest.name.strip())

declare_entity(
    entity_name='Component Manifest Constraints',
    constraints_for='Node//Artifact//Atom//Spec Atom//Manifest//Component Manifest',
    instance_relation_constraints={'CONTAINED_BY': {'target_entity_paths': ('Node//Artifact//Component',), 'targets_per_source': 1}},
    instance_check=check_component_manifest,
)
```
