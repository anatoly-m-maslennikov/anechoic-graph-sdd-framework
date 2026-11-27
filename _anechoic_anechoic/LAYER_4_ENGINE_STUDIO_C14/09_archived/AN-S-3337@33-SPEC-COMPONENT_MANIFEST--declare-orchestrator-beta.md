---
atom_family: SPEC
atom_id: AN-S-3337
container:
  component: C14
tier: 1
context:
  template: component_manifest
  lens: SPEC
state:
  status: "archived"
  version: 33
  updated_at: "2026-11-27T18:25:19.395007+00:00"
---
## Summary

Declare Orchestrator Beta

## Component Identity

```python
from anechoic.model import ComponentManifest

ComponentManifest(
    component_id='C68',
    name='Orchestrator Beta',
    lens_whitelist=['DES', 'SPEC', 'IO/API/IPC'],
)
```

## Component Boundaries

```python
{'code': {'imports': {'only': ['archive_jobs',
                               'metrics__shared.is_measurement_input',
                               'ADAPTERS_C30__shared.console_state_path',
                               'container_settings__pub.CONTAINER_SETTINGS_FILENAME',
                               'container_settings__pub.parse_container_settings',
                               'settings_carrier__pub.parse_settings_carrier',
                               'ADAPTERS_C30__shared.CEILINGS',
                               'ADAPTERS_C30__shared.ReadContext',
                               'ADAPTERS_C30__shared.native_carrier_path',
                               'ADAPTERS_C30__shared.native_header_view',
                               'ADAPTERS_C30__shared.parse_carrier',
                               'ADAPTERS_C30__shared.source_body',
                               'ADAPTERS_C30__shared.is_ontology_model_source',
                               'ADAPTERS_C30__shared.ontology_component_path',
                               'ATOM_LIFECYCLE__shared.ticket_status_options',
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
                               'ORCHESTRATOR_beta_C68__shared.WorkerIngestionFailure']},
          'exports': {'archive_jobs': {'private': ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests']},
                      'ORCHESTRATOR_beta_C68__shared.ArchiveCoverageLost': {'private': ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests']},
                      'ORCHESTRATOR_beta_C68__shared.ArchiveInputsChanged': {'private': ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests']},
                      'ORCHESTRATOR_beta_C68__shared.DeltaRequiresReconciliation': {'private': ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests']},
                      'ORCHESTRATOR_beta_C68__shared.PollComplete': {'private': ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests']},
                      'ORCHESTRATOR_beta_C68__shared.WorkerIngestionFailure': {'private': ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests']},
                      'lifecycle_queries.lifecycle_context': {'private': ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests']},
                      'lifecycle_queries.lifecycle_sql': {'private': ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests']},
                      'ORCHESTRATOR_beta_C68__shared': {'private': ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests']},
                      'ORCHESTRATOR_beta_C68__shared.Flow': {'private': ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests']},
                      'ORCHESTRATOR_beta_C68__shared.GenerationJobs': {'private': ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests']}}},
 'io': {'server': {'project_peer_owner': {'transport': 'cli',
                                          'runner': 'managed_python',
                                          'module': 'ORCHESTRATOR_beta_C68.project_peer_owner',
                                          'stack': 'beta_next',
                                          'supervisor': 'C21',
                                          'arguments': 'selected Project '
                                                       'binding and peer '
                                                       'settings',
                                          'readiness': 'peers.ready after '
                                                       'bound peers '
                                                       'start'},
                   'shared_peer_owner': {'transport': 'newline-delimited '
                                                      'JSON over private '
                                                      'Unix socket',
                                         'runner': 'managed_python',
                                         'module': 'ORCHESTRATOR_beta_C68.shared_peer_owner',
                                         'stack': 'beta_next',
                                         'supervisor': 'C21',
                                         'arguments': ['--socket',
                                                       '<owner-socket>',
                                                       '--host-settings',
                                                       '<settings>'],
                                         'operations': ['select',
                                                        'status',
                                                        'lease']},
                   'jobs': {'transport': 'http',
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
                                          'optional paired '
                                          '--worker-socket and '
                                          '--worker-load-seconds'],
                            'routes': ['GET /health',
                                       'POST /jobs/build',
                                       'POST /jobs/abort',
                                       'POST /jobs/lifecycle',
                                       'GET /jobs/worker-runs'],
                            'build_request': ['instance_id',
                                              'root',
                                              'control_root',
                                              'manifest_path',
                                              'manifest_sha256',
                                              'project_prefix'],
                            'optional_build_field': 'refresh_target',
                            'abort_fields': ['instance_id', 'run_id'],
                            'active_fields': ['run_id', 'worker_alive'],
                            'abort_scope': ['cold generation',
                                            'accepted warm capture'],
                            'worker_mode': ['warm', 'cold'],
                            'build_timings': ['worker_seconds',
                                              'admission_seconds'],
                            'optional_delta_field': 'delta_path_count',
                            'lifecycle_request': 'build binding plus name '
                                                 'and arguments',
                            'lifecycle_result': ['lifecycle',
                                                 'write_state',
                                                 'projection']}},
        'client': {'snapshot_worker': {'component': 'C69',
                                       'transport': 'cli',
                                       'parent_env': 'ANECHOIC_BETA_WORKER_PARENT_PID'},
                   'warm_ticket_delta': {'component': 'C69',
                                         'interface': 'warm_ticket_delta'},
                   'warm_indexed_lifecycle': {'component': 'C69',
                                              'interface': 'warm_indexed_lifecycle'},
                   'lifecycle_worker': {'component': 'C69',
                                        'interface': 'task_lifecycle',
                                        'parent_env': 'ANECHOIC_BETA_WORKER_PARENT_PID'},
                   'database': {'component': 'C71',
                                'transport': 'http',
                                'routes': ['GET /generation/reuse',
                                           'GET /structure',
                                           'PUT /generation',
                                           'PUT /generation/native',
                                           'PUT /generation/native-delta',
                                           'POST /flow/events',
                                           'POST /database']}}},
 'state': {'reads': ['pinned Project binding',
                     'Project source change events',
                     'code and dependency file events when the Graph is '
                     'enabled'],
           'writes': ['active build, lifecycle request, latest Worker '
                      'outcome and admitted input proof in memory',
                      'candidate peer, warm Worker, and shared lease '
                      'state']}}
```

## Component Contract

### Run a pinned Beta snapshot Worker

#### Guarantee

For `beta_next`, own the selected Project's peer pair and warm Worker.
Report readiness after its bound peers start. Stop them with their owner.
Apply AN-S-5192 to shared-mode Project selection, status, and leases.

Establish watcher coverage before capture. Admit the pinned Current and
Draft base and replay events through the completed observation before
Ready or affected writes. Leave later events queued. Require source proof
for uncovered inputs. On coverage loss, reconcile affected inputs and
broaden capture if the scope is unknown. Log failed source checks once to
stderr with run ID, phase, wait, and Project-relative evidence. Distinguish
source changes from coverage loss.

Serialize live builds and Kernel admissions at startup and on watched
changes. Watch Graph inputs when enabled. Follow AN-S-3389 for Archive
readiness. Load Archive in a separate Worker while live changes proceed.
Keep Archive pending until Kernel admits it. Report progress, failure,
and the separate readiness and Archive timing.

Use one Manifest Builder per Project. Coalesce input changes during a
build into one follow-up for the newest observed inputs. Submit its exact
Model and Structure together. Mark affected data pending and block
affected writes until that generation is admitted.

Serialize pinned rebuild requests with source changes. Requests for the
same target share one admission and result map. Reply after the fresh
generation is admitted, with result replacements or a typed failure.
Report the active build and latest outcome.

Serialize lifecycle jobs with generation builds. Use one admitted Kernel
generation for SQL allocation, history, containment, and replacements.
Supply the Model rules and Structure. Use an isolated warm Worker child
when configured, and coordinated capture for Ticket tree or Model changes.
Return the write outcome and native delta admission result. Preserve known
effects on projection failure. A lost response leaves the effect unknown.
Block further writes until complete recapture confirms the source.
Never repeat a write automatically.

Reuse the input proof only after Kernel acceptance. For watcher refresh,
pin the proof and the matching Structure when needed for non-Ticket work.
Submit native refresh, or native and Graph refresh, against the named base.
Full-build if the base changed. Explicit rebuilds use the full build path. Retry native
currentness failures with backoff. Report a failed Code Analyzer restart
as a build issue. Ignore delayed watcher events only when source matches
the retained effect, including absence.

Default to Incremental Startup after Worker verification and Kernel
confirmation of a compatible checkpoint. Reuse unchanged projection and
apply verified offline Current and Draft deltas. Apply AN-S-3334 to
checkpoint verification and Graph-only changes. Full reload also applies
when the database or checkpoint is missing.

Use native Ticket notifications when available and polling for missed
or other events. Send both rename paths. Collect events for 20 ms after
the first. For up to 32 distinct Ticket paths, wait for the warm Worker
at most the measured cold-load time, then use a fresh Worker if needed.
Send 33 through 1,024 paths to one fresh Worker. Broaden capture or
reconcile when the paths or base cannot be verified. Keep one admission
in flight per Project. Report mode, capture including startup, admission
time, and path count for the latest successful delta.

Report the active run ID and liveness of its cold Worker or warm child.
Wait for completion or explicit abort. Stop the aborted process group
and report that outcome. Exclude writes and Kernel admission from abort.
Bind fresh Workers to the current Orchestrator. They stop their process
group on owner loss. A replacement admits from Project state.

Send one causal trace of the trigger, accepted changes, effects, output,
and any clock-driven retry to the bound Kernel. Log publication errors.

#### References

AN-S-3337 and AN-T-2958.
