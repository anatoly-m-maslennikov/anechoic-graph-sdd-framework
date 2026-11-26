---
atom_family: SPEC
atom_id: AN-S-3108
container:
  component: C9
tier: 2
context:
  lens: SPEC
relations:
  IS_REPLACEMENT_FOR:
  - AN-S-3125
  - AN-S-3132
  - AN-S-3133
  - AN-S-3149
state:
  status: "archived"
  version: 3
  updated_at: "2026-11-25T01:29:27.952535+00:00"
---

## Summary

Declare Project Manifest Spec Template

## Semantics

A Project Manifest describes a Project.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from __future__ import annotations

from dataclasses import field
from anechoic.formal_claims import declare_template
from anechoic.model import Manifest, Project

def check_project_manifest(manifest: ProjectManifest) -> bool:
    mcp = manifest.parameters.get("project_mcp", {})
    return bool(
        manifest.name.strip()
        and manifest.prefix.strip()
        and len(manifest.parameters) + 2 + (manifest.lens_whitelist is not None) <= 20
        and type(mcp) is dict
        and type(mcp.get("release_workflows_enabled", False)) is bool
    )

@declare_template(tier=-1, container=Project, instance_check=check_project_manifest)
class ProjectManifest(Manifest):
    name: str
    prefix: str
    parameters: dict[str, object] = field(default_factory=dict)
```
