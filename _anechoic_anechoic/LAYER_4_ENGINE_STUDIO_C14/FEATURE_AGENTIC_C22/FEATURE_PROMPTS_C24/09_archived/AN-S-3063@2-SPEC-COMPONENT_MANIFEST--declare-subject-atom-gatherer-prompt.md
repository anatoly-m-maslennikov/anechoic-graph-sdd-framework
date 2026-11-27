---
atom_family: SPEC
atom_id: AN-S-3063
container:
  component: C24
tier: 4
context:
  template: component_manifest
  lens: SPEC
state:
  status: "archived"
  version: 2
  updated_at: "2026-11-26T15:54:01.204948+00:00"
---

## Summary

Declare SUBJECT_ATOM_GATHERER_PROMPT

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C57',
        name='SUBJECT_ATOM_GATHERER_PROMPT',
        lens_whitelist=['DES'],
        boundaries={'code': {'imports': {'only': []}, 'exports': {}},
                    'state': {'reads': [], 'writes': []}},
    ),
)
```

## Boundary scope

This definition covers subject_atom_gatherer.prompt.md, an unseparated asset in FEATURE_SUBJECT_TREE_ATOM_REWRITE_PROMPT. The carrier instructs a consumer; it does not perform the described reads or state effects.
