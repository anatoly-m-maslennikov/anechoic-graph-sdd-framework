---
atom_family: SPEC
atom_id: AN-S-3052
container:
  component: C15
tier: 0
context:
  template: component_manifest
  lens: SPEC
state:
  status: "archived"
  version: 3
  updated_at: "2026-11-22T10:35:15.288671+00:00"
---

## Summary

Declare CODEX_HOOK

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C49',
        name='CODEX_HOOK',
        lens_whitelist=['DES'],
        boundaries={
            'code': {
                'imports': {'only': []},
                'exports': {
                    'FEATURE_CODEX_HOOK__shared': None,
                    'FEATURE_CODEX_HOOK__shared.main': None,
                },
            },
        },
    ),
)
```
