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
  status: archived
  version: 5
  updated_at: '2026-11-22T11:23:40.206159+00:00'
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
                'exports': {
                    'FEATURE_CODEX_EXTENSION__shared': None,
                    'FEATURE_CODEX_EXTENSION__shared.call': None,
                    'FEATURE_CODEX_EXTENSION__shared.list_resources': None,
                    'FEATURE_CODEX_EXTENSION__shared.read_resource': None,
                    'FEATURE_CODEX_EXTENSION__shared.tools': None,
                },
            },
            'state': {
                'reads': ['bundled compatibility probe HTML', 'bundled Workbench MCP App HTML'],
                'writes': [],
            },
        },
    ),
)
```
