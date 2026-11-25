---
atom_family: SPEC
atom_id: AN-S-3064
container:
  component: C24
tier: 4
context:
  template: component_manifest
  lens: SPEC
state:
  status: archived
  version: 2
  updated_at: '2026-11-22T11:23:40.206159+00:00'
---

## Summary

Declare SUBJECT_TREE_ATOM_REWRITE_PROMPT

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C56',
        name='SUBJECT_TREE_ATOM_REWRITE_PROMPT',
        lens_whitelist=['DES'],
        boundaries={'code': {'imports': {'only': []}, 'exports': {}},
                    'state': {'reads': [], 'writes': []}},
    ),
)
```

## Boundary scope

This definition covers subject_tree_atom_rewrite.prompt.md and compact_spec_rewrite.prompt.md. These carriers instruct a consumer; they do not perform the described reads, Draft writes, or state effects.
