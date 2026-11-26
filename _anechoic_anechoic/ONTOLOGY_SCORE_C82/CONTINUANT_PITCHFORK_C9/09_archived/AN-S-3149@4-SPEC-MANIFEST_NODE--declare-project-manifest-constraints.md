---
atom_family: SPEC
atom_id: AN-S-3149
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_node
state:
  status: "archived"
  version: 4
  updated_at: '2026-11-24T23:18:33.190860+00:00'
---

## Summary

Declare Project Manifest Constraints

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Artifact//SSOT//Prescribed/Content/Atom//Specification//Manifest//Project Manifest.Constraints

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import NodeConstraints, Project, ProjectManifest

def check_project_manifest(manifest: ProjectManifest) -> bool:
    mcp = manifest.parameters.get("project_mcp", {})
    return bool(
        manifest.name.strip()
        and manifest.prefix.strip()
        and len(manifest.parameters) + 2 + (manifest.lens_whitelist is not None) <= 20
        and type(mcp) is dict
        and type(mcp.get("release_workflows_enabled", False)) is bool
    )

class Constraints(NodeConstraints):
    bearer = ProjectManifest
    instance_check = check_project_manifest
    instance_relation_constraints = {'IS_CONTAINED_BY': {'target_entity_paths': (Project,), 'targets_per_source': 1}}
```
