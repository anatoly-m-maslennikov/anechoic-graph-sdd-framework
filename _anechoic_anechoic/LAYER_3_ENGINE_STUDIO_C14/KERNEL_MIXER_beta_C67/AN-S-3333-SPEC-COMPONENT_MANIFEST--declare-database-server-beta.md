---
atom_family: SPEC
atom_id: AN-S-3333
container:
  component: C67
tier: 4
context:
  template: component_manifest
  lens: SPEC
state:
  status: active
  version: 2
  updated_at: '2026-11-22T11:23:40.206159+00:00'
---
## Summary

Declare Database Server Beta

## Purpose

Serve read-only queries on an admitted Project snapshot.

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C71',
        name='Database Server Beta',
        lens_whitelist=['DES', 'SPEC'],
        boundaries={'code': {'imports': {'only': []}}, 'io': {'server': {'database_api': {'transport': 'http', 'socket': 'private Unix socket', 'path': 'LAYER_3_ENGINE_STUDIO_C14/KERNEL_MIXER_beta_C67/DATABASE_SERVER_beta_C71/DATABASE_SERVER_beta_C71__pub.py', 'arguments': ['--socket', '<socket>', '--snapshot', '<snapshot>', '--instance-id', '<instance-id>', '--manifest-sha256', '<manifest-sha256>'], 'routes': {'health': 'GET /health', 'query': 'POST /database'}, 'query_fields': ['instance_id', 'sql']}}}, 'state': {'reads': ['pinned Atom snapshot'], 'writes': ['per-Project in-memory database']}},
    ),
)
```
