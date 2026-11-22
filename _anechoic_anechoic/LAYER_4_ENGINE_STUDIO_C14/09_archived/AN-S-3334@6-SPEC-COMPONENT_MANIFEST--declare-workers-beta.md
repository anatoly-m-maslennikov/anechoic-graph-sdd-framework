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
  version: 6
  updated_at: "2026-11-22T16:04:33.665080+00:00"
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
                                                       'generation receipt and Graph on stdout',
                                             'generation_snapshot': 'version 2 with native revisions and relations',
                                             'arguments': ['optional --generation-dir '
                                                           '<empty-directory>'],
                                             'module': 'WORKERS_beta_C69.WORKERS_beta_C69__shared'}},
                'client': {'manifest_build': {'component_seed': 'CS4', 'transport': 'cli'},
                           'native_snapshot': {'component': 'C30',
                                               'interface': 'native_snapshot'},
                           'realization_graph': {'component': 'C61',
                                                 'interface': 'build_graph'}}},
         'state': {'reads': ['pinned Project Manifest and native Atom carriers'],
                   'writes': ['staged artifacts for a generation build']}},
    ),
)
```
