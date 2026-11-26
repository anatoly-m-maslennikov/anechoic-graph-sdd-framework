---
atom_family: SPEC
atom_id: AN-S-3078
container:
  component: C31
tier: 4
context:
  template: component_manifest
  lens: SPEC
state:
  status: draft
  version: 3
  updated_at: '2026-11-22T11:23:40.206159+00:00'
---

## Summary

Declare PROJECTION_ACTIONS

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C37',
        name='PROJECTION_ACTIONS',
        lens_whitelist=['DES', 'DevOps', 'QA', 'SWD'],
        boundaries={'io': {'server': {'derive_entity_projection': {'outcomes': {
            'projection_returned': {
                'must_effect': [('projection_result', 'returned'), ('source_lineage', 'returned')],
                'forbid_effect': ['authority_write', 'projection_write'],
            },
            'frontier_rejected': {
                'must_effect': [('frontier_error', 'returned')],
                'forbid_effect': ['projection_result', 'authority_write', 'projection_write'],
            },
        }}}}},
    ),
)
```
