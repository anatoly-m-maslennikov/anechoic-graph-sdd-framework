---
atom_family: SPEC
atom_id: AN-S-3061
container:
  component: C24
tier: 4
context:
  template: component_manifest
  lens: SPEC
state:
  status: active
  version: 3
  updated_at: "2026-11-24T23:12:55.813309+00:00"
---

## Summary

Declare ATOM_AUTHORING_PROMPT

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C54',
        name='ATOM_AUTHORING_PROMPT',
        lens_whitelist=['DES'],
        boundaries={'code': {'imports': {'only': []}},
                    'state': {'reads': [], 'writes': []}},
    ),
)
```

## Boundary scope

This definition covers atom_authoring.prompt.md. The carrier instructs a consumer; it does not perform the described lifecycle calls or state effects.
