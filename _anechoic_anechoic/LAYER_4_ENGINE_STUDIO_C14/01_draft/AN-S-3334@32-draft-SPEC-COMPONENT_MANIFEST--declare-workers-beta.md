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
  status: draft
  version: 32
  updated_at: "2026-11-25T00:00:00+00:00"
---
## Summary

Declare Workers Beta

## Purpose

Build a transient Project snapshot and staged generation for Kernel.
Run an admitted Ticket lifecycle operation in a short-lived process.

The `atom_snapshot` success effects below cover cold full generation.
Stage captured Project Spec rows in C71 under the Project binding. Pass
the rows returned for that snapshot ID to the Spec Engine before compilation.
Other modes remain as declared by the endpoint and its Contract.

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
        boundaries={'code': {'exports': {'WORKERS_beta_C69__shared.python_code_units': {'private': ['LAYER_4_ENGINE_STUDIO_C14/WORKERS_beta_C69/WORKERS_beta_C69__tests',
                                                                                'C74']},
                     'WORKERS_beta_C69__shared.python_context_restoration': {'private': ['LAYER_4_ENGINE_STUDIO_C14/WORKERS_beta_C69/WORKERS_beta_C69__tests']},
                     'WORKERS_beta_C69__shared.python_import_order': {'private': ['LAYER_4_ENGINE_STUDIO_C14/WORKERS_beta_C69/WORKERS_beta_C69__tests']}},
         'imports': {'only': ['metrics__shared.code_rows',
                              'ADAPTERS_C30__shared.capture_carrier_delta',
                              'ADAPTERS_C30__shared.UnrepresentableCarrierDelta',
                              'FEATURE_TOOLS__shared.indexed_draft_runner',
                              'ADAPTERS_C30__shared.capture_ticket_delta',
                              'ADAPTERS_C30__shared.prepare_generation_snapshot',
                              'ADAPTERS_C30__shared.NativeSnapshotChanged',
                              'ADAPTERS_C30__shared.owned_temporary_root',
                              'ADAPTERS_C30__shared.mark_startup_timing',
                              'ADAPTERS_C30__shared.native_carrier_hashes',
                              'import_graph__shared.run_graph_build',
                              'import_graph__shared.graph_input_signature',
                              'manifest_build_CS4__shared.manifest_input_signature',
                              'WORKERS_beta_C69__shared.python_context_restoration',
                              'WORKERS_beta_C69__shared.python_import_order',
                              'WORKERS_beta_C69__shared.python_code_units']}},
         'io': {'server': {'atom_snapshot': {'outcomes': {'succeeded': {'must_effect': [('C69.model_structure', 'compiled'), ('C69.snapshot_graph', 'captured'), ('C69.artifacts', 'sealed'), ('C69.receipt', 'returned_with_artifact_seals')]}},
                                             'transport': 'cli',
                                             'runner': 'managed_python',
                                             'input': 'JSON Project binding or managed binding and reuse proof on stdin',
                                             'managed_parent_env': 'ANECHOIC_BETA_WORKER_PARENT_PID',
                                             'optional_managed_field_sets': [['paths'], ['structure']],
                                             'output': 'JSON Atom snapshot or paired '
                                                       'generation receipt and Graph, or base generation and native snapshot with digest on stdout',
                                             'optional_refresh_field_sets': [['paths'], ['graph', 'graph_sha256', 'reuse']],
                                             'ticket_delta_max_paths': 1024,
                                             'carrier_hashes': 'complete snapshot or present delta paths',
                                             'unchanged_result': ['base_generation', 'unchanged'],
                                             'generation_snapshot': 'version 2 with native revisions and relations',
                                             'arguments': ['optional --generation-dir '
                                                           '<empty-directory>'],
                                             'module': 'WORKERS_beta_C69.WORKERS_beta_C69__shared'},
                           'warm_ticket_delta': {'transport': 'newline-delimited JSON over private Unix socket',
                                                 'runner': 'managed_python',
                                                 'module': 'WORKERS_beta_C69.warm_worker',
                                                 'arguments': ['--socket', '<private-runtime-socket>'],
                                                 'health': {'request': ['kind'], 'reply': ['ready', 'pid']},
                                                 'ticket_delta_max_paths': 32,
                                                 'capture_fields': ['kind', 'start_by', 'binding', 'reuse', 'paths'],
                                                 'accepted_reply': ['accepted', 'pid when accepted'],
                                                 'completion_reply': ['result'],
                                                 'cancel': 'client write-half close'},
                           'warm_indexed_lifecycle': {'transport': 'newline-delimited JSON over private Unix socket',
                                                      'module': 'WORKERS_beta_C69.warm_worker',
                                                      'kind': 'indexed_lifecycle',
                                                      'fields': ['kind', 'start_by', 'request'],
                                                      'request': 'task_lifecycle with indexed_task or lifecycle_context',
                                                      'accepted_reply': ['accepted', 'pid when accepted'],
                                                      'completion_reply': ['result'],
                                                      'cancel': 'client write-half close'},
                           'task_lifecycle': {'transport': 'cli', 'runner': 'managed_python',
                                              'module': 'WORKERS_beta_C69.lifecycle_worker',
                                              'managed_parent_env': 'ANECHOIC_BETA_WORKER_PARENT_PID',
                                              'input_fields': ['binding', 'name', 'arguments', 'base_generation', 'structure_sha256'],
                                              'optional_inputs': ['indexed_task', 'lifecycle_context'],
                                              'operations': ['atom_lifecycle_create_draft',
                                                             'atom_lifecycle_update',
                                                             'atom_lifecycle_promote_draft',
                                                             'atom_lifecycle_change_status',
                                                             'atom_lifecycle_archive',
                                                             'atom_lifecycle_direct_update',
                                                             'atom_lifecycle_create_asset'],
                                              'output': 'native lifecycle outcome and effects on stdout'},
                           'worker_ticket_lifecycle': {'outcomes': {
                               'delta_returned': {
                                   'must_effect': (('C69.lifecycle_result', 'outcome_and_delta_returned'), ('C16', 'lifecycle_requested'), ('C16', 'outcome_and_file_effects_received')),
                                   'forbid_effect': ('C69.full_generation',),
                               },
                               'projection_failed': {
                                   'must_effect': (('C69.projection_error', 'reported'), ('C16', 'lifecycle_requested'), ('C16', 'outcome_and_file_effects_received')),
                                   'forbid_effect': ('C69.lifecycle_result', 'C69.full_generation'),
                               },
                           }}},
                'client': {'task_lifecycle': {'component': 'C16', 'interface': 'task_lifecycle', 'transport': 'cli'},
                           'manifest_build': {'component_seed': 'CS4', 'transport': 'cli'},
                           'spec_snapshot': {'component': 'C71', 'interface': 'database_api', 'transport': 'http'},
                           'native_snapshot': {'component': 'C30',
                                               'interface': 'native_snapshot'},
                           'realization_graph': {'component': 'C61', 'interface': 'build_graph',
                                                 'module': 'WORKERS_beta_C69.realization_graph'}}},
         'state': {'reads': ['pinned Project Manifest and native Atom carriers'],
                   'writes': ['staged artifacts for a generation build', 'admitted Ticket effects through C16']}},
    ),
)
```
