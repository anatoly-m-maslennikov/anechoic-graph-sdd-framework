---
atom_family: SPEC
atom_id: AN-S-3149
container:
  component: C9
tier: 2
context:
  lens: SPEC
state:
  status: archived
  version: 1
  updated_at: '2026-11-20T14:42:07.157939+00:00'
---

## Summary

Declare Project Manifest Constraints

## Claim scope

MODEL//ANECHOIC <+ Node//Artifact//Atom//Spec Atom//Manifest//Project Manifest.Constraints

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ProjectManifest

def check_project_manifest(manifest: ProjectManifest) -> bool:
    return bool(manifest.name.strip() and manifest.prefix.strip() and len(manifest.parameters) + 2 + (manifest.lens_whitelist is not None) <= 20)

declare_entity(
    entity_name='Project Manifest Constraints',
    constraints_for='Node//Artifact//Atom//Spec Atom//Manifest//Project Manifest',
    instance_relation_constraints={'CONTAINED_BY': {'target_entity_paths': ('Node//Artifact//Component//Project',), 'targets_per_source': 1}},
    instance_check=check_project_manifest,
)
```
