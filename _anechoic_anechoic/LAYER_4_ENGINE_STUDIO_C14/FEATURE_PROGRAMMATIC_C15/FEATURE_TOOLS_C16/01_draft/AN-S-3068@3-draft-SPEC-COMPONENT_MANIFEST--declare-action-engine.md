---
atom_family: SPEC
atom_id: AN-S-3068
container:
  component: C16
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

Declare ACTION_ENGINE

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C34',
        name='ACTION_ENGINE',
        lens_whitelist=['DES', 'DevOps', 'QA', 'SWD'],
        boundaries={'io': {'server': {'control_background_services': {'outcomes': {
            'dry_run_reported': {'forbid_effect': ['mutation', 'service_state']},
            'registry_rejected': {'forbid_effect': ['mutation', 'service_state']},
            'empty_registry_noop': {'forbid_effect': ['mutation', 'service_state']},
        }}}}},
    ),
)
```
