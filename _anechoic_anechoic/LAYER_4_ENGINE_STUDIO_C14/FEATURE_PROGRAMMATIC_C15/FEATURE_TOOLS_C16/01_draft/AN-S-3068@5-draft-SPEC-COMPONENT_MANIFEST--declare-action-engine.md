---
atom_family: SPEC
atom_id: AN-S-3068
container:
  component: C16
tier: 1
context:
  template: component_manifest
  lens: SPEC
state:
  status: draft
  version: 5
  updated_at: '2026-11-27T11:22:36.001339+00:00'
---

## Summary

Declare ACTION_ENGINE

## Purpose

Specify Action Engine control of registered background services. AN-S-1214@7 requires commands to preserve accepted work and reach the declared safe boundaries.

## Component Identity

```python
from anechoic.model import ComponentManifest

ComponentManifest(
    component_id='C34',
    name='ACTION_ENGINE',
    lens_whitelist=['DES', 'DevOps', 'QA', 'SWD'],
)
```

## Component Boundaries

```python
{'code': {'imports': [], 'exports': {}}, 'io': {'server': {}}, 'state': {'reads': [], 'writes': []}}
```

## Component Contract

### Reserve ACTION_ENGINE

#### Guarantee

C34 retains the registered-service control obligations in AN-S-1214@7. Its current Manifest declares no callable entry point. AN-S-3056@67 assigns native Atom lifecycle execution to C16.

```python group
declare_group_contract(
    roles={},
    entry_points=(),
)
```
