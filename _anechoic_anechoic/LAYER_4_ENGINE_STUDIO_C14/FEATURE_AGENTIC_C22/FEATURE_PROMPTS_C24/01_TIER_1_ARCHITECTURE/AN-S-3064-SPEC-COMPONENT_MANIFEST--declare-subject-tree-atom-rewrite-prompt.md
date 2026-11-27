---
atom_family: SPEC
atom_id: AN-S-3064
container:
  component: C24
tier: 1
context:
  template: component_manifest
  lens: SPEC
state:
  status: "active"
  version: 5
  updated_at: "2026-11-26T15:52:29.915537+00:00"
---

## Summary

Declare SUBJECT_TREE_ATOM_REWRITE_PROMPT

## Component Identity

```python
from anechoic.model import ComponentManifest

ComponentManifest(
    component_id='C56',
    name='SUBJECT_TREE_ATOM_REWRITE_PROMPT',
    lens_whitelist=['DES'],
)
```

## Component Boundaries

```python
{'code': {'imports': {'only': []}, 'exports': {}},
 'state': {'reads': [], 'writes': []}}
```

## Boundary scope

This definition covers subject_tree_atom_rewrite.prompt.md and compact_spec_rewrite.prompt.md. These carriers instruct a consumer; they do not perform the described reads, Draft writes, or state effects.

## Component Contract

### Guide subject tree rewrite

#### Guarantee

Guide an agent to rebuild gathered Subject Atom sets from pinned sources and retain traceability through Drafts.
