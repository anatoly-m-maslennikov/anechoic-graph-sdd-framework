---
atom_family: SPEC
atom_id: AN-S-3063
container:
  component: C24
tier: 1
context:
  template: component_manifest
  lens: SPEC
state:
  status: "active"
  version: 5
  updated_at: "2026-11-26T15:52:29.905667+00:00"
---

## Summary

Declare SUBJECT_ATOM_GATHERER_PROMPT

## Component Identity

```python
from anechoic.model import ComponentManifest

ComponentManifest(
    component_id='C57',
    name='SUBJECT_ATOM_GATHERER_PROMPT',
    lens_whitelist=['DES'],
)
```

## Component Boundaries

```python
{'code': {'imports': {'only': []}, 'exports': {}},
 'state': {'reads': [], 'writes': []}}
```

## Boundary scope

This definition covers subject_atom_gatherer.prompt.md, an unseparated asset in FEATURE_SUBJECT_TREE_ATOM_REWRITE_PROMPT. The carrier instructs a consumer; it does not perform the described reads or state effects.

## Component Contract

### Guide subject atom gathering

#### Guarantee

Guide gathering of pinned Current source Atoms, parent and dependency context, and gaps for a Subject-tree rewrite.
