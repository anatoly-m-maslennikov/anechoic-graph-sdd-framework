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
  status: draft
  version: 7
  updated_at: '2026-11-25T16:17:18+00:00'
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
            'io': {
                'server': {
                    'codex_extension_read_resource': {'outcomes': {
                        'succeeded': {'must_effect': (('C48.resource_html', 'returned'),)},
                        'failed': {'must_effect': (('C48.resource_error', 'unknown_ui_resource'),), 'forbid_effect': ('C48.resource_html',)},
                    }},
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
