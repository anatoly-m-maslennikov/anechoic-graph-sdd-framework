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
  status: "active"
  version: 4
  updated_at: "2026-11-22T11:57:56.679244+00:00"
---
## Summary

Declare Database Server Beta

## Purpose

Own the accepted Project generation and serve read-only queries.

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
        boundaries={'code': {'imports': {'only': ['CS5', 'CS6']}},
         'io': {'server': {'database_api': {'transport': 'http',
                                            'socket': 'private Unix socket',
                                            'arguments': ['--socket',
                                                          '<socket>',
                                                          '--instance-id',
                                                          '<instance-id>',
                                                          '--manifest-sha256',
                                                          '<manifest-sha256>'],
                                            'routes': {'health': 'GET /health',
                                                       'query': 'POST /database',
                                                       'admit': 'PUT /generation',
                                                       'model': 'GET /model',
                                                       'structure': 'GET /structure'},
                                            'query_fields': ['instance_id', 'sql'],
                                            'admit_fields': ['instance_id',
                                                             'snapshot',
                                                             'receipt',
                                                             'model',
                                                             'structure'],
                                            'runner': 'managed_python',
                                            'module': 'KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.DATABASE_SERVER_beta_C71__pub'}}},
         'state': {'reads': ['attested Project generation'],
                   'writes': ['accepted Project rows and paired artifacts in the '
                              'database']}},
    ),
)
```
