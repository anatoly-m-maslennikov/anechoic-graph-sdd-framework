---
atom_family: SPEC
atom_id: AN-S-3342
container:
  component: C00
tier: 4
context:
  template: component_manifest
  lens: SPEC
state:
  status: active
  version: 1
  updated_at: '2026-11-22T12:00:09.602716+00:00'
---

## Summary

Declare Environments

## Purpose

Define the requirements for the environments that run, test, release, and
install Anechoic. Each Project child owns its environment and dependency lock.

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C72',
        name='Environments',
        layer=3,
        lens_whitelist=['DevOps'],
    ),
)
```
