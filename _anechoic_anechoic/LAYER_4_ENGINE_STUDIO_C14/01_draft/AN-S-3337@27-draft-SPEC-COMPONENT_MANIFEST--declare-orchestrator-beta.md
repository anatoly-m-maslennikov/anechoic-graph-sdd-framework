---
atom_family: SPEC
atom_id: AN-S-3337
container:
  component: C14
tier: 4
context:
  template: component_manifest
  lens: SPEC
state:
  status: draft
  version: 27
  updated_at: "2026-11-24T23:12:55.813309+00:00"
---
## Summary

Declare Orchestrator Beta

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C68',
        name='Orchestrator Beta',
        lens_whitelist=['DES', 'SPEC'],
        boundaries={'code': {'exports': {'ORCHESTRATOR_beta_C68__shared': {'private': ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests']},
                     'ORCHESTRATOR_beta_C68__shared.ArchiveCoverageLost': {'private': ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests']},
                     'ORCHESTRATOR_beta_C68__shared.ArchiveInputsChanged': {'private': ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests']},
                     'ORCHESTRATOR_beta_C68__shared.DeltaRequiresReconciliation': {'private': ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests']},
                     'ORCHESTRATOR_beta_C68__shared.Flow': {'private': ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests']},
                     'ORCHESTRATOR_beta_C68__shared.GenerationJobs': {'private': ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests']},
                     'ORCHESTRATOR_beta_C68__shared.PollComplete': {'private': ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests']},
                     'ORCHESTRATOR_beta_C68__shared.WorkerIngestionFailure': {'private': ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests']},
                     'lifecycle_queries.lifecycle_context': {'private': ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests']},
                     'lifecycle_queries.lifecycle_sql': {'private': ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests']}},
         'imports': {'only': ['metrics__shared.is_measurement_input',
                              'ADAPTERS_C30__shared.mark_startup_timing',
                              'ORCHESTRATOR_beta_C68__shared',
                              'ORCHESTRATOR_beta_C68__shared.Flow',
                              'ORCHESTRATOR_beta_C68__shared.GenerationJobs',
                              'lifecycle_queries.lifecycle_context',
                              'lifecycle_queries.lifecycle_sql',
                              'ORCHESTRATOR_beta_C68__shared.ArchiveCoverageLost',
                              'ORCHESTRATOR_beta_C68__shared.ArchiveInputsChanged',
                              'ORCHESTRATOR_beta_C68__shared.DeltaRequiresReconciliation',
                              'ORCHESTRATOR_beta_C68__shared.PollComplete',
                              'ORCHESTRATOR_beta_C68__shared.WorkerIngestionFailure']}},
         'io': {'server': {'jobs': {'transport': 'http',
                                    'socket': 'private Unix socket',
                                    'runner': 'managed_python',
                                    'module': 'ORCHESTRATOR_beta_C68.ORCHESTRATOR_beta_C68__shared',
                                    'arguments': ['--socket',
                                                  '<socket>',
                                                  '--instance-id',
                                                  '<instance-id>',
                                                  '--binding-file',
                                                  '<pinned-project-binding>',
                                                  '--database-socket',
                                                  '<kernel-socket>',
                                                  'optional --watch-code',
                                                  'optional paired --worker-socket and --worker-load-seconds'],
                                    'routes': ['GET /health',
                                               'POST /jobs/build',
                                               'POST /jobs/abort',
                                               'POST /jobs/lifecycle',
                                               'GET /jobs/worker-runs'],
                                    'build_request': ['instance_id', 'root', 'control_root', 'manifest_path',
                                                      'manifest_sha256', 'project_prefix'],
                                    'optional_build_field': 'refresh_target',
                                    'abort_fields': ['instance_id', 'run_id'],
                                    'active_fields': ['run_id', 'worker_alive'],
                                    'abort_scope': ['cold generation', 'accepted warm capture'],
                                    'worker_mode': ['warm', 'cold'],
                                    'build_timings': ['worker_seconds', 'admission_seconds'],
                                    'optional_delta_field': 'delta_path_count',
                                    'lifecycle_request': 'build binding plus name and arguments',
                                    'lifecycle_result': ['lifecycle', 'write_state', 'projection']},
                           'beta_lifecycle_delta_projection': {'outcomes': {
                               'write_unknown': {
                                   'must_effect': (
                                       ('C69.write_reply', 'missing'),
                                       ('C68.write_gate', 'blocked'),
                                       ('C68.write_outcome', 'unknown'),
                                   ),
                                   'forbid_effect': ('C68.automatic_write_repeat', 'C71.delta', 'C68.write_request'),
                               },
                               'write_blocked': {
                                   'must_effect': (
                                       ('C68.write_gate', 'blocked'),
                                       ('C68.write_request', 'rejected'),
                                   ),
                                   'forbid_effect': ('C69.lifecycle_dispatch', 'C71.delta'),
                               },
                               'projected': {
                                   'must_effect': (
                                       ('C68.write_outcome', 'recorded'),
                                       ('C71.delta', 'committed'),
                                       ('C68.write_outcome', 'reported'),
                                   ),
                               },
                               'worker_projection_failed': {
                                   'must_effect': (('C68.worker_projection_error', 'reported'),),
                                   'forbid_effect': ('C71', 'C71.delta', 'C68.automatic_write_repeat'),
                               },
                               'projection_rejected': {
                                   'must_effect': (
                                       ('C68.write_outcome', 'recorded'),
                                       ('C71.previous_generation', 'retained'),
                                       ('C68.write_outcome', 'reported'),
                                   ),
                                   'forbid_effect': ('C71.delta',),
                               },
                           }},
                           'beta_startup_catch_up': {'outcomes': {
                               'live_catch_up_confirmed': {
                                   'must_effect': [('current_and_draft', 'catch_up_confirmed')],
                               },
                           }},
                           'project_peer_owner': {
                               'transport': 'cli',
                               'runner': 'managed_python',
                               'module': 'ORCHESTRATOR_beta_C68.project_peer_owner',
                               'stack': 'beta_next',
                               'supervisor': 'C21',
                               'arguments': 'selected Project binding and peer settings',
                               'readiness': 'peers.ready after bound peers start',
                           },
                           'shared_peer_owner': {
                               'transport': 'newline-delimited JSON over private Unix socket',
                               'runner': 'managed_python',
                               'module': 'ORCHESTRATOR_beta_C68.shared_peer_owner',
                               'stack': 'beta_next',
                               'supervisor': 'C21',
                               'arguments': ['--socket', '<owner-socket>', '--host-settings', '<settings>'],
                               'operations': ['select', 'status', 'lease'],
                           },
                           'generate': {'outcomes': {
                               'succeeded': {'must_effect': [('C69.artifacts', 'sealed'),
                                                             ('C71.generation', 'committed'),
                                                             ('C68.replacement_ids', 'returned')]},
                               'failed': {'forbid_effect': ['C68.replacement_ids']},
                               'aborted': {'forbid_effect': ['C71.generation', 'C68.replacement_ids']},
                           }}},
                'client': {'snapshot_worker': {'component': 'C69', 'interface': 'atom_snapshot', 'transport': 'cli',
                                                'parent_env': 'ANECHOIC_BETA_WORKER_PARENT_PID'},
                           'warm_ticket_delta': {'component': 'C69', 'interface': 'warm_ticket_delta'},
                           'warm_indexed_lifecycle': {'component': 'C69', 'interface': 'warm_indexed_lifecycle'},
                           'lifecycle_worker': {'component': 'C69', 'interface': 'task_lifecycle',
                                                'parent_env': 'ANECHOIC_BETA_WORKER_PARENT_PID'},
                           'database': {'component': 'C71',
                                        'interface': 'database_api',
                                        'transport': 'http',
                                        'routes': ['GET /generation/reuse', 'GET /structure', 'PUT /generation', 'PUT /generation/native',
                                                   'PUT /generation/native-delta', 'POST /flow/events', 'POST /database']}}},
         'state': {'reads': ['pinned Project binding',
                             'Project source change events',
                             'code and dependency file events when the Graph is enabled'],
                   'writes': ['active build, lifecycle request, latest Worker outcome and admitted input proof in memory',
                              'candidate peer, warm Worker, and shared lease state']}},
    ),
)
```
