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
  status: "active"
  version: 28
  updated_at: "2026-11-26T15:52:27.709987+00:00"
---
## Summary

Declare Orchestrator Beta

## Component Identity

```python
from anechoic.model import ComponentManifest

ComponentManifest(
    component_id='C68',
    name='Orchestrator Beta',
    lens_whitelist=['DES', 'SPEC'],
)
```

## Component Boundaries

```python
{'code': {'imports': {'only': ['metrics__shared.is_measurement_input',
                               'ADAPTERS_C30__shared.console_state_path',
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
          'exports': {'ORCHESTRATOR_beta_C68__shared.ArchiveCoverageLost': {'private': ['LAYER_4_ENGINE_STUDIO_C14/ORCHESTRATOR_beta_C68/ORCHESTRATOR_beta_C68__tests']},
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

For `beta_next`, own the selected Project peer pair and its warm Worker.
The Project owner publishes readiness only after its bound peers start.
Keep the peers bound to the owner process and stop them when it exits.

For shared `beta_next`, select Projects and provide status and leases over
a private Unix socket. Keep lease state with the peer owner. Release a
lease when its request ends.

Wait for the Project watcher's coverage baseline before startup capture.
Queue covered changes during capture. When coverage holds, admit the
pinned Current and Draft capture as the base.

Replay the changes through the completed observation before reporting
readiness or admitting affected writes. Leave later events queued for
normal refresh.

If coverage is lost, reconcile the affected inputs with source proof.
Use a broader capture when the affected scope cannot be verified.
Require source proof for inputs outside watcher coverage.

For each failed source check, write one bounded stderr record with the
run ID, phase, wait time, and available Project-relative evidence.
Distinguish source changes from missing watcher coverage.

Load Archived Atoms in a separate Worker while the live lane handles
source changes. Report Archive progress and failures separately. Wait
for complete history before admitting lifecycle writes.

Serialize live builds and admissions. Start a live build at Project
startup and after changes to watched Project sources. Watch code and
dependency inputs when the Project enables its Realization Graph.

Offer the generation to Kernel for admission. Report the active build
and latest outcome. Retry a build with backoff when changed inputs
prevent the required source proof.

Keep one active Manifest Builder per selected Project. Within the
pinned owner, coalesce Manifest input changes during a build into one
follow-up for the newest observed inputs. Submit its exact Model and
Structure for admission together.

Mark affected data pending and block affected writes until Kernel
admits the generation for those inputs.

For a rebuild request matching the pinned Project, complete a fresh
generation before replying. Serialize rebuild requests with source changes.
Return the admitted generation and requested result replacements, or a
typed failure. Overlapping requests for the same target share one
admission and result map.

Serialize each accepted lifecycle job with generation builds. Require an
admitted base. Admit the Worker’s native carrier delta against that base.
Return the recorded write outcome and projection result. Preserve known
effects on projection failure. If the Worker response is lost, report
the write outcome as unknown. Never repeat a write automatically.

Select single-Atom lifecycle facts from one admitted Kernel generation.
Use SQL for allocation, revision history, containment, and replacements.
Give the Worker the admitted Structure and needed Model rules. Run the
write in an isolated child of the warm Worker when configured. Use the
coordinated capture path for Ticket tree moves and Model input changes.
Block writes after an unconfirmed write until Kernel admits a complete
source snapshot.

Retain recent admitted carrier receipts by path. Ignore delayed watcher
events only while the file contents or absence match the recorded effect.

Retain the input proof only after Kernel accepts the generation. On a
watcher event, supply that proof to a short-lived Worker. For a
change outside the Ticket delta path, supply the Kernel Structure
when its generation matches the proof. Submit a native or native
and Realization Graph refresh against that base. Run a full build
if the base changed. Explicit rebuilds use the full build path.

Report a failed Code Analyzer restart as a build issue and reserve the
automatic generation retry for native source currentness failures.

Use Incremental Startup by default with a compatible persisted checkpoint
from Kernel. Require Worker verification and Kernel confirmation of the
base. Reuse an unchanged projection and admit the verified offline
Current and Draft additions, edits, moves, and deletions.

Use a full reload when the projection database or checkpoint is missing,
the checkpoint is incompatible or cannot be verified, or a Model,
Structure, or compiler schema input changed. When only Realization
Graph inputs changed, request a Graph rebuild using the admitted
Model and Structure.

Run Archive catch-up in the background. Mark Archive pending while it
catches up, including when prior checkpoint rows are visible. Clear
that state only after Kernel confirms complete Archive. Report elapsed
time to live readiness and Archive completion separately.

Use native notifications for Ticket files where available. Retain
polling for missed changes and other inputs. Send both paths for a
Ticket rename. For supported Ticket-only changes, submit the delta
against the accepted base. Reconcile when Kernel rejects that base
or the available evidence cannot establish a safe delta.

Collect watcher events for 20 ms after the first event in a batch.
For a supported batch of up to 32 distinct Ticket paths, wait for
the warm Worker up to the measured cold load time. Use a fresh
Worker if that wait expires or the warm Worker cannot return a delta.

For 33 through 1,024 distinct Ticket paths, send the whole batch to
one fresh Worker. Use the existing broader capture when the path
set cannot be verified. Keep one admission in flight per Project.

Report the Worker mode, capture time including startup, admission
time, and delta path count for the latest successful delta.

Report the active run ID and the liveness of its cold Worker or
accepted warm child. Wait for completion or an abort for that run.
Stop its process group and report the terminal outcome as aborted.
Keep lifecycle writes and Kernel admission outside this operation.

Bind fresh Workers to the current Orchestrator process.
A Worker stops its group if that owner exits. A replacement
Orchestrator starts admission from Project state.

Record the generation trigger, output, and observed side effects as one
causal trace. Include accepted file changes and the clock-driven retry.
Send observations to the bound Kernel. Report publication errors to stderr.

#### References

AN-S-3337 and AN-T-2958.
