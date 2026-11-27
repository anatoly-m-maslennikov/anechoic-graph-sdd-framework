---
atom_family: SPEC
atom_id: AN-S-3076
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

Declare ATOM_ACTIONS

## Purpose

Specify logical Atom Actions. AN-S-2397@5 separates read-only Find over an explicit Scope and lifecycle frontier from Check and single-target Change.

## Component Identity

```python
from anechoic.model import ComponentManifest

ComponentManifest(
    component_id='C35',
    name='ATOM_ACTIONS',
    lens_whitelist=['DES', 'QA'],
)
```

## Component Boundaries

```python
{'code': {'imports': [], 'exports': {}}, 'io': {'server': {}}, 'state': {'reads': [], 'writes': []}}
```

## Component Contract

### Reserve ATOM_ACTIONS

#### Guarantee

Find returns matching Atom identities and selected current values within the admitted frontier. Each mutation binds one explicit Atom and its expected state. C35 declares no direct entry point. AN-S-3056@67 assigns native Atom lifecycle execution to C16.

#### Claim

##### Formal Claim

```python group
declare_group_contract(
    roles={},
    entry_points=(),
)
```
