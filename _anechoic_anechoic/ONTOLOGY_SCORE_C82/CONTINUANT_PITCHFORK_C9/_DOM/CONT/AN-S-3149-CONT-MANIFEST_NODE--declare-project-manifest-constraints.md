---
atom_family: SPEC
atom_id: AN-S-3149
concern:
  subject: Constraints
  path: Model/Graph/Node//Artifact//SSOT//Prescribed/Content/Atom//Specification//Manifest//Project Manifest
  relation: is_property_of
container:
  component: C9
tier: 2
context:
  template: manifest_node
  lens: DOM/CONT
state:
  status: "active"
  version: 6
  updated_at: "2026-11-26T15:52:33.143410+00:00"
---

## Summary

Declare Project Manifest Constraints

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
    node.constraints.instance_check = check_project_manifest
    node.constraints.instance_relations = {'IS_CONTAINED_BY': {'target_entity_paths': (Project,), 'targets_per_source': 1}}
```
