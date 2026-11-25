---
atom_family: SPEC
atom_id: AN-S-3058
container:
  component: C43
tier: 4
context:
  template: component_manifest
  lens: SPEC
state:
  status: active
  version: 6
  updated_at: "2026-11-24T23:12:55.813309+00:00"
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
            'code': {
                'imports': {'only': []},
            },
            'state': {
                'reads': ['bundled compatibility probe HTML', 'bundled Workbench MCP App HTML'],
                'writes': [],
            },
        },
    ),
)
```
