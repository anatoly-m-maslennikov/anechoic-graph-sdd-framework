---
atom_family: SPEC
atom_id: AN-S-4703
container:
  component: C00
tier: 1
context:
  template: component_manifest
  lens: SPEC
state:
  status: "active"
  version: 3
  updated_at: "2026-11-26T15:52:24.492000+00:00"
---

## Summary

Declare DevOps

## Purpose

Build Engine Studio and own Environments and Release.

## Component Identity

```python
from anechoic.model import ComponentManifest

ComponentManifest(
    component_id='C80',
    name='DevOps',
    layer=3,
    lens_whitelist=['DevOps'],
)
```
