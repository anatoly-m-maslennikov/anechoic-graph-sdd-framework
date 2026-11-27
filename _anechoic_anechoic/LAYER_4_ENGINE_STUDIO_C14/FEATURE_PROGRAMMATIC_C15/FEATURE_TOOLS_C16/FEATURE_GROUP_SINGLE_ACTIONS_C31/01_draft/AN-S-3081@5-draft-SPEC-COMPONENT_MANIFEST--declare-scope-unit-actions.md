---
atom_family: SPEC
atom_id: AN-S-3081
container:
  component: C31
tier: 1
context:
  template: component_manifest
  lens: SPEC
state:
  status: draft
  version: 5
  updated_at: '2026-11-27T10:55:20+00:00'
---

## Summary

Declare SCOPE_UNIT_ACTIONS

## Purpose

Reserve Scope Unit Actions as a Component.

## Component Identity

```python
from anechoic.model import ComponentManifest

ComponentManifest(
    component_id='C36',
    name='SCOPE_UNIT_ACTIONS',
    lens_whitelist=['DES'],
)
```

## Component Boundaries

```python
{'code': {'imports': [], 'exports': {}}, 'io': {'server': {}}, 'state': {'reads': [], 'writes': []}}
```

## Component Contract

### Reserve scope unit actions

#### Guarantee

This Component has no declared children or callable entry points. A callable boundary requires admission.

#### Claim

##### Formal Claim

```python group
declare_group_contract(
    roles={},
    entry_points=(),
)
```
