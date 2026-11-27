---
atom_family: SPEC
atom_id: AN-S-3115
container:
  component: C9
tier: 2
context:
  lens: SPEC
relations:
  IS_REPLACEMENT_FOR:
  - AN-S-3142
  - AN-S-3143
  - AN-S-3144
  - AN-S-3145
  - AN-S-3155
state:
  status: "archived"
  version: 5
  updated_at: '2026-11-24T11:27:17+00:00'
---

## Summary

Declare Component Seed Manifest Spec Template

## Semantics

A Component Seed Manifest records a Component Seed's identity, purpose, solution, and optional boundaries.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from __future__ import annotations

from anechoic.formal_claims import declare_template
from anechoic.model import Component, Lens, SpecAtom

def check_component_seed_manifest(spec: ComponentSeedManifest) -> bool:
    return bool(spec.component_seed_id.startswith("CS") and spec.component_seed_id[2:].isascii()
                and spec.component_seed_id[2:].isdigit() and spec.purpose.strip() and spec.solution.strip())

@declare_template(container=Component, lens=Lens.SPEC, instance_check=check_component_seed_manifest)
class ComponentSeedManifest(SpecAtom):
    component_seed_id: str
    purpose: str
    solution: str
    boundaries: dict[str, object] | None = None
```
