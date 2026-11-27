---
atom_family: SPEC
atom_id: AN-S-3078
container:
  component: C31
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

Declare PROJECTION_ACTIONS

## Purpose

Specify reproducible, non-authoritative Entity and Term graph Projections under AN-S-275@23.

## Component Identity

```python
from anechoic.model import ComponentManifest

ComponentManifest(
    component_id='C37',
    name='PROJECTION_ACTIONS',
    lens_whitelist=['DES', 'DevOps', 'QA', 'SWD'],
)
```

## Component Boundaries

```python
{'code': {'imports': [], 'exports': {}}, 'io': {'server': {}}, 'state': {'reads': [], 'writes': []}}
```

## Component Contract

### Reserve PROJECTION_ACTIONS

#### Guarantee

Ordinary generation is read-only. Persistence requires an admitted destination and atomically replaces one Projection Carrier for one source frontier. C37 declares no direct Projection entry point.

#### Claim

##### Formal Claim

```python group
declare_group_contract(
    roles={},
    entry_points=(),
)
```
