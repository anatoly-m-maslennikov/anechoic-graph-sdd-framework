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
  status: draft
  version: 4
  updated_at: '2026-11-25T21:41:25.002107+00:00'
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
        boundaries={'io': {'server': {'provide_project_environments': {'outcomes': {'environments_available': {'must_effect': [('engine_environment', 'available'), ('release_environment', 'available'), ('setup_environment', 'available')]}}}}}},
    ),
)
```
