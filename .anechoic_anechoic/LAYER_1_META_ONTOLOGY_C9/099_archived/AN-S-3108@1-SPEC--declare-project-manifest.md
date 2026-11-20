---
atom_family: SPEC
atom_id: AN-S-3108
structure:
  container:
    component: C9
context:
  lens: SPEC
state:
  status: archived
  version: 1
  updated_at: '2026-11-20T11:17:59+00:00'
---

## Summary

Declare Project Manifest

## Claim scope

MODEL//ANECHOIC <+ Node//Artifact//Atom//Spec Atom//Manifest//Project Manifest

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Manifest
from dataclasses import field

class ProjectManifest(Manifest):
    tier: int = field(metadata={"allowed_values": (-1,)})
    name: str
    prefix: str
    parameters: dict[str, object] = field(default_factory=dict)

def check_project_manifest(manifest: ProjectManifest) -> bool:
    return bool(manifest.name.strip() and manifest.prefix.strip() and len(manifest.parameters) + 2 + (manifest.lens_whitelist is not None) <= 20)

declare_entity(
    entity_name="Project Manifest",
    entity_class=ProjectManifest,
    instance_relation_constraints={
        "CONTAINED_BY": {"target_entity_paths": ("Node//Artifact//Component//Project",), "targets_per_source": 1},
    },
    instance_check=check_project_manifest,
)
```
