---
atom_family: SPEC
atom_id: AN-S-3149
container:
  component: C9
tier: 2
context:
  lens: SPEC
state:
  status: active
  version: 2
  updated_at: '2026-11-20T20:37:23.155399+00:00'
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
    mcp = manifest.parameters.get("project_mcp", {})
    return bool(
        manifest.name.strip()
        and manifest.prefix.strip()
        and len(manifest.parameters) + 2 + (manifest.lens_whitelist is not None) <= 20
        and type(mcp) is dict
        and type(mcp.get("release_workflows_enabled", False)) is bool
    )

declare_entity(
    entity_name='Project Manifest Constraints',
    constraints_for='Node//Artifact//Atom//Spec Atom//Manifest//Project Manifest',
    instance_relation_constraints={'CONTAINED_BY': {'target_entity_paths': ('Node//Artifact//Component//Project',), 'targets_per_source': 1}},
    instance_check=check_project_manifest,
)
```
