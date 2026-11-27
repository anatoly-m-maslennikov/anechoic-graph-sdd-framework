---
atom_family: SPEC
atom_id: AN-S-3051
container:
  component: C15
tier: 1
context:
  template: component_manifest
  lens: SPEC
state:
  status: draft
  version: 6
  updated_at: '2026-11-27T11:22:36.001339+00:00'
---

## Summary

Declare APPS

## Purpose

Group App placeholders under Programmatic. AN-S-2112@1 declares the legacy WORKBENCH Scope Unit CA-SU-43 under APPS. AN-S-3046@6 declares the IWE Console Component C43 directly under C14.

## Component Identity

```python
from anechoic.model import ComponentManifest

ComponentManifest(
    component_id='C20',
    name='APPS',
    lens_whitelist=['DES', 'DevOps', 'QA', 'SPEC', 'SWD'],
)
```

## Component Boundaries

```python
{'code': {'imports': [], 'exports': {}}, 'io': {'server': {}}, 'state': {'reads': [], 'writes': []}}
```

## Component Contract

### Hold App placeholders

#### Guarantee

C20 exposes no executable App entry point and declares no Component children. The legacy Scope Unit declaration in AN-S-2112@1 applies only to that Scope Unit.

#### Claim

##### Formal Claim

```python group
declare_group_contract(
    roles={},
    entry_points=(),
)
```

## Details

C20 is a grouping placeholder. Its current App directories contain no executable entry point; it declares no code, IO, or state boundary.
