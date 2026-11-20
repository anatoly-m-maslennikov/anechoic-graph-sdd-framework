---
identity:
  atom_id: AN-S-3109
context:
  container:
    component: C9
  lens: SPEC
state:
  status: archived
  version: 1
  updated_at: '2026-11-20T11:17:59+00:00'
---

## Summary

Declare Component Manifest

## Claim scope

MODEL//ANECHOIC <+ Node//Artifact//Atom//Spec Atom//Manifest//Component Manifest

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Manifest
from dataclasses import field

class ComponentManifest(Manifest):
    tier: int = field(metadata={"allowed_values": (0,)})
    component_id: str
    name: str
    layer: int | None = None

def check_component_manifest(manifest: ComponentManifest) -> bool:
    return bool(manifest.component_id.strip() and manifest.name.strip())

declare_entity(
    entity_name="Component Manifest",
    entity_class=ComponentManifest,
    instance_relation_constraints={
        "CONTAINED_BY": {"target_entity_paths": ("Node//Artifact//Component",), "targets_per_source": 1},
    },
    instance_check=check_component_manifest,
)
```
