---
atom_family: SPEC
atom_id: AN-S-3334
container:
  component: C14
tier: 4
context:
  template: component_manifest
  lens: SPEC
state:
  status: "archived"
  version: 4
  updated_at: "2026-11-22T13:08:05.936426+00:00"
---
## Summary

Declare Workers Beta

## Purpose

Build a transient Project snapshot and staged generation for Kernel.

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C69',
        name='Workers Beta',
        lens_whitelist=['DES', 'SPEC'],
        boundaries={'code': {'imports': {'only': []}},
         'io': {'server': {'atom_snapshot': {'transport': 'cli',
                                             'runner': 'managed_python',
                                             'input': 'JSON Project binding on stdin',
                                             'output': 'JSON Atom snapshot or paired '
                                                       'generation receipt on stdout',
                                             'arguments': ['optional --generation-dir '
                                                           '<empty-directory>'],
                                             'module': 'WORKERS_beta_C69.WORKERS_beta_C69__shared'}},
                'client': {'manifest_build': {'component_seed': 'CS4', 'transport': 'cli'},
                           'native_snapshot': {'component': 'C30',
                                               'interface': 'native_snapshot'}}},
         'state': {'reads': ['pinned Project Manifest and native Atom carriers'],
                   'writes': ['staged artifacts for a generation build']}},
    ),
)
```
