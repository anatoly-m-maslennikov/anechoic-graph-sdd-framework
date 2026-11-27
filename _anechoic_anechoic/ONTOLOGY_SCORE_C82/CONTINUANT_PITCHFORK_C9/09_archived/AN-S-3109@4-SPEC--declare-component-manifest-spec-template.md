---
atom_family: SPEC
atom_id: AN-S-3109
container:
  component: C9
tier: 2
context:
  lens: SPEC
relations:
  IS_REPLACEMENT_FOR:
  - AN-S-3126
  - AN-S-3135
  - AN-S-3136
  - AN-S-3137
  - AN-S-3138
  - AN-S-3150
state:
  status: "archived"
  version: 4
  updated_at: '2026-11-24T11:27:02+00:00'
---

## Summary

Declare Component Manifest Spec Template

## Semantics

A Component Manifest describes a Component.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from __future__ import annotations

from anechoic.formal_claims import declare_template
from anechoic.model import Component, Lens, Manifest

def check_component_manifest(manifest: ComponentManifest) -> bool:
    return bool(manifest.component_id.strip() and manifest.name.strip())

@declare_template(tier=4, container=Component, lens=Lens.SPEC, instance_check=check_component_manifest)
class ComponentManifest(Manifest):
    component_id: str
    name: str
    layer: int | None = None
    boundaries: dict[str, object] | None = None
```
