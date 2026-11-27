---
atom_family: SPEC
atom_id: AN-S-3342
container:
  component: C80
tier: 4
context:
  template: component_manifest
  lens: SPEC
state:
  status: "archived"
  version: 3
  updated_at: "2026-11-26T15:54:00.676806+00:00"
---

## Summary

Declare Environments

## Purpose

Define the requirements for the environments that run, test, release, and
install Anechoic. This layer holds the separate uv projects and locks for
Engine Studio, Release, and Setup.

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C72',
        name='Environments',
        layer=1,
        lens_whitelist=['DevOps'],
    ),
)
```
