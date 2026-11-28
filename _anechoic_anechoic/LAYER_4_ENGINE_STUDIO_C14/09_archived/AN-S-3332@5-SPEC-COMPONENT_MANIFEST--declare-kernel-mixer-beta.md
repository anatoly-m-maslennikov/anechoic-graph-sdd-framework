---
atom_family: SPEC
atom_id: AN-S-3332
container:
  component: C14
tier: 1
context:
  template: component_manifest
  lens: SPEC
state:
  status: archived
  version: 5
  updated_at: "2026-11-27T18:25:19.395007+00:00"
---
## Summary

Declare Kernel Mixer Beta

## Purpose

Contain Beta's Database Server and the read-only Model and Structure Hosts
in one local Kernel process. The Backend starts and stops that process;
the Database Server owns its storage and serves the private API.

## Component Identity

```python
from anechoic.model import ComponentManifest

ComponentManifest(
    component_id='C67',
    name='Kernel Mixer Beta',
    lens_whitelist=['DES', 'SPEC'],
)
```

## Component Boundaries

```python
{'io': {'server': {'database_api': {'component': 'C71',
                                    'transport': 'http',
                                    'socket': 'private Unix socket',
                                    'module': 'KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.DATABASE_SERVER_beta_C71__shared',
                                    'routes': {'health': 'GET /health',
                                               'schema': 'GET /schema',
                                               'ingestion_issues': 'GET '
                                                                   '/ingestion/issues',
                                               'replace_ingestion_issues': 'PUT '
                                                                           '/ingestion/issues',
                                               'query': 'POST /database',
                                               'workspace': 'POST '
                                                            '/workspace',
                                               'rebuild_results': 'POST '
                                                                  '/results/rebuild',
                                               'admit': 'PUT /generation',
                                               'reuse': 'GET '
                                                        '/generation/reuse',
                                               'flow_events': 'POST '
                                                              '/flow/events',
                                               'admit_native': 'PUT '
                                                               '/generation/native',
                                               'admit_native_delta': 'PUT '
                                                                     '/generation/native-delta',
                                               'model': 'GET /model',
                                               'structure': 'GET '
                                                            '/structure'}}}},
 'state': {'reads': ['bound Project instance and accepted generation'],
           'writes': ['process-local Database Server connection and '
                      'lock']}}
```

## Component Contract

### Serve an admitted Beta Project generation

#### Guarantee

Keep the Database Server and the Model and Structure Hosts within the
Kernel process. Bind the server to one Project instance. Admit the paired
artifacts and Project snapshot as one generation; retain the prior generation
if admission fails.

For a request bound to that instance, serve the accepted Model or Structure
bytes with their generation ID. Before admission, report that no generation
is available. Reject a request for another instance.

#### References

AN-S-3332, AN-S-3335, AN-S-3343, and AN-S-3344.
