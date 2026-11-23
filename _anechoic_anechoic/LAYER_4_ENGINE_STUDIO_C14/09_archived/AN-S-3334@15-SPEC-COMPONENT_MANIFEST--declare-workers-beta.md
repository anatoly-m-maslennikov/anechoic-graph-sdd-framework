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
  version: 15
  updated_at: "2026-11-22T19:07:59.632908+00:00"
---
## Summary

Declare Workers Beta

## Purpose

Build a transient Project snapshot and staged generation for Kernel.
Run an admitted Task or Epic lifecycle operation in a short-lived process.

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
        boundaries={'code': {'imports': {'only': ['ADAPTERS_C30__shared.capture_ticket_delta',
                                           'import_graph__shared.run_graph_build',
                                           'import_graph__shared.graph_input_signature',
                                           'manifest_build_CS4__shared.manifest_input_signature',
                                           'WORKERS_beta_C69__shared.python_context_restoration',
                                           'WORKERS_beta_C69__shared.python_import_order',
                                           'WORKERS_beta_C69__shared.python_code_units']},
                          'exports': {
                              'WORKERS_beta_C69__shared.python_context_restoration': {'private': ['LAYER_4_ENGINE_STUDIO_C14/WORKERS_beta_C69/WORKERS_beta_C69__tests']},
                              'WORKERS_beta_C69__shared.python_import_order': {'private': ['LAYER_4_ENGINE_STUDIO_C14/WORKERS_beta_C69/WORKERS_beta_C69__tests']},
                              'WORKERS_beta_C69__shared.python_code_units': {'private': [
                              'LAYER_4_ENGINE_STUDIO_C14/WORKERS_beta_C69/WORKERS_beta_C69__tests']}}},
         'io': {'server': {'atom_snapshot': {'transport': 'cli',
                                             'runner': 'managed_python',
                                             'input': 'JSON Project binding or managed binding, reuse proof, and optional Ticket paths on stdin',
                                             'output': 'JSON Atom snapshot or paired '
                                                       'generation receipt and Graph, or base generation and native snapshot with digest and optional path scope, on stdout',
                                             'generation_snapshot': 'version 2 with native revisions and relations',
                                             'arguments': ['optional --generation-dir '
                                                           '<empty-directory>'],
                                             'module': 'WORKERS_beta_C69.WORKERS_beta_C69__shared'},
                           'task_lifecycle': {'transport': 'cli', 'runner': 'managed_python',
                                              'module': 'WORKERS_beta_C69.lifecycle_worker',
                                              'input_fields': ['binding', 'name', 'arguments'],
                                              'operations': ['atom_lifecycle_create_draft',
                                                             'atom_lifecycle_update',
                                                             'atom_lifecycle_promote_draft',
                                                             'atom_lifecycle_change_status',
                                                             'atom_lifecycle_archive'],
                                              'output': 'native lifecycle outcome and effects on stdout'}},
                'client': {'task_lifecycle': {'component': 'C16', 'interface': 'task_lifecycle'},
                           'manifest_build': {'component_seed': 'CS4', 'transport': 'cli'},
                           'native_snapshot': {'component': 'C30',
                                               'interface': 'native_snapshot'},
                           'realization_graph': {'component': 'C61', 'interface': 'build_graph',
                                                 'module': 'WORKERS_beta_C69.realization_graph'}}},
         'state': {'reads': ['pinned Project Manifest and native Atom carriers'],
                   'writes': ['staged artifacts for a generation build', 'admitted Task and Epic effects through C16']}},
    ),
)
```
