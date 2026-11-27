---
atom_family: SPEC
atom_id: AN-S-3342
container:
  component: C80
tier: 1
context:
  template: component_manifest
  lens: SPEC
state:
  status: "active"
  version: 5
  updated_at: "2026-11-26T15:52:25.371451+00:00"
---

## Summary

Declare Environments

## Purpose

Define the requirements for the environments that run, test, release, and
install Anechoic. This layer holds the separate uv projects and locks for
Engine Studio, Release, and Setup.

## Component Identity

```python
from anechoic.model import ComponentManifest

ComponentManifest(
    component_id='C72',
    name='Environments',
    layer=1,
    lens_whitelist=['DevOps'],
)
```
