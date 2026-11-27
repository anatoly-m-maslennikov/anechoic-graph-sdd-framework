---
atom_family: SPEC
atom_id: AN-S-3071
container:
  component: C16
tier: 1
context:
  template: component_manifest
  lens: SPEC
state:
  status: draft
  version: 4
  updated_at: '2026-11-27T11:22:36.001339+00:00'
---

## Summary

Declare SINGLE_ACTIONS

## Purpose

Group the declared Single Action families by target. An Atom mutation binds one explicit Atom. Read-only Find uses the explicit Scope and lifecycle frontier admitted by AN-S-2397@5.

## Component Identity

```python
from anechoic.model import ComponentManifest

ComponentManifest(
    component_id='C31',
    name='SINGLE_ACTIONS',
    lens_whitelist=['DES', 'SPEC', 'SWD'],
)
```

## Component Boundaries

```python
{'code': {'imports': [], 'exports': {}}, 'io': {'server': {}}, 'state': {'reads': [], 'writes': []}}
```

## Component Contract

### Group single actions by target

#### Guarantee

Each Atom mutation takes one explicit Atom target. The owning Workflow sequences mutations for separate targets under AN-S-2422@12. Read-only Find can return several matches from its selected frontier. Each child owns its operation, failure and state rules.

#### Claim

##### Formal Claim

```python group
declare_group_contract(
    roles={'atom_actions': 'C35', 'scope_unit_actions': 'C36', 'projection_actions': 'C37', 'journal_actions': 'C38', 'project_actions': 'C39', 'queue_actions': 'C40'},
    entry_points=(),
)
```
