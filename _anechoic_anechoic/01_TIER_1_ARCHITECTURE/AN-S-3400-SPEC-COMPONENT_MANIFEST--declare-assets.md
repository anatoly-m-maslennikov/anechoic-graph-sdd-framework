---
atom_family: SPEC
atom_id: AN-S-3400
container:
  component: C00
tier: 1
context:
  template: component_manifest
  lens: SPEC
state:
  status: "active"
  version: 3
  updated_at: "2026-11-26T15:52:24.040834+00:00"
---

## Summary

Declare Assets

## Purpose

Maintain the source files for Anechoic brand assets.

## Component Identity

```python
from anechoic.model import ComponentManifest

ComponentManifest(
    component_id='C78',
    name='Assets',
    lens_whitelist=['DES', 'SPEC'],
)
```
