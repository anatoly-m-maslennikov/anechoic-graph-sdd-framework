---
atom_family: SPEC
atom_id: AN-S-3058
structure:
  container:
    component: C43
  tier: 0
context:
  template: component_manifest
  lens: SPEC
state:
  status: "active"
  version: 2
  updated_at: "2026-11-21T12:26:54.944132+00:00"
---

## Summary

Declare CODEX_EXTENSION

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C48',
        name='CODEX_EXTENSION',
        lens_whitelist=['DES', 'DevOps', 'QA', 'SWD'],
        boundaries={
            'code_access': {
                'imports': [],
                'exports': {
                    'FEATURE_CODEX_EXTENSION__family_pub': None,
                    'FEATURE_CODEX_EXTENSION__family_pub.call': None,
                    'FEATURE_CODEX_EXTENSION__family_pub.list_resources': None,
                    'FEATURE_CODEX_EXTENSION__family_pub.read_resource': None,
                    'FEATURE_CODEX_EXTENSION__family_pub.tools': None,
                },
            },
        },
    ),
)
```
