---
atom_family: SPEC
atom_id: AN-S-3334
container:
  component: C14
tier: 1
context:
  template: component_manifest
  lens: SPEC
state:
  status: active
  version: 35
  updated_at: '2026-11-27T13:09:34.995824+00:00'
---
## Summary

Declare Workers Beta

## Purpose

Build a transient Project snapshot and staged generation for Kernel.
Run an admitted Ticket lifecycle operation in a short-lived process.

## Component Identity

```python
from anechoic.model import ComponentManifest

ComponentManifest(
    component_id='C69',
    name='Workers Beta',
    lens_whitelist=['DES', 'SPEC'],
)
```

## Component Boundaries

```python
{'code': {'imports': {'only': ['generation_batches._capture_archive',
                               'managed_request._ArchiveCapture',
                               'WORKERS_beta_C69__shared',
                               'spec_staging._stage_spec_rows',
                               'WORKERS_beta_C69__shared._compile_ingested',
                               'manifest_build_CS4__shared._COMPILER_SOURCE_DIRECTORIES',
                               'manifest_build_CS4__shared._REVIEWED_CLAIMS',
                               'manifest_build_CS4__shared._compiler_sha256',
                               'manifest_build_CS4__shared.compile_generation',
                               'compile_project__pub',
                               'ADAPTERS_C30__shared.status_domains',
                               'metrics__shared.code_rows',
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
                               'WORKERS_beta_C69__shared.python_code_units']},
          'exports': {'generation_batches._capture_archive': {'private': ['LAYER_4_ENGINE_STUDIO_C14/WORKERS_beta_C69/WORKERS_beta_C69__tests']},
                      'managed_request._ArchiveCapture': {'private': ['LAYER_4_ENGINE_STUDIO_C14/WORKERS_beta_C69/WORKERS_beta_C69__tests']},
                      'WORKERS_beta_C69__shared': {'private': ['LAYER_4_ENGINE_STUDIO_C14/WORKERS_beta_C69/WORKERS_beta_C69__tests']},
                      'spec_staging._stage_spec_rows': {'private': ['LAYER_4_ENGINE_STUDIO_C14/WORKERS_beta_C69/WORKERS_beta_C69__tests']},
                      'WORKERS_beta_C69__shared._compile_ingested': {'private': ['LAYER_4_ENGINE_STUDIO_C14/WORKERS_beta_C69/WORKERS_beta_C69__tests']},
                      'WORKERS_beta_C69__shared.python_context_restoration': {'private': ['LAYER_4_ENGINE_STUDIO_C14/WORKERS_beta_C69/WORKERS_beta_C69__tests']},
                      'WORKERS_beta_C69__shared.python_import_order': {'private': ['LAYER_4_ENGINE_STUDIO_C14/WORKERS_beta_C69/WORKERS_beta_C69__tests']},
                      'WORKERS_beta_C69__shared.python_code_units': {'private': ['LAYER_4_ENGINE_STUDIO_C14/WORKERS_beta_C69/WORKERS_beta_C69__tests',
                                                                                 'C74']}}},
 'io': {'server': {'atom_snapshot': {'transport': 'cli',
                                     'runner': 'managed_python',
                                     'input': 'JSON Project binding or '
                                              'managed binding and reuse '
                                              'proof on stdin',
                                     'managed_parent_env': 'ANECHOIC_BETA_WORKER_PARENT_PID',
                                     'optional_managed_field_sets': [['paths'],
                                                                     ['structure'],
                                                                     ['model_source'],
                                                                     ['batch_full']],
                                     'output': 'JSON Atom snapshot or '
                                               'paired generation receipt '
                                               'and Graph, or base '
                                               'generation and native '
                                               'snapshot with digest on '
                                               'stdout',
                                     'optional_refresh_field_sets': [['paths'],
                                                                     ['graph',
                                                                      'graph_sha256',
                                                                      'reuse']],
                                     'ticket_delta_max_paths': 1024,
                                     'carrier_hashes': 'complete snapshot '
                                                       'or present delta '
                                                       'paths',
                                     'unchanged_result': ['base_generation',
                                                          'unchanged'],
                                     'generation_snapshot': 'version 2 '
                                                            'with native '
                                                            'revisions '
                                                            'and '
                                                            'relations',
                                     'arguments': ['optional '
                                                   '--generation-dir '
                                                   '<empty-directory>'],
                                     'module': 'WORKERS_beta_C69.WORKERS_beta_C69__shared'},
                   'warm_ticket_delta': {'transport': 'newline-delimited '
                                                      'JSON over private '
                                                      'Unix socket',
                                         'runner': 'managed_python',
                                         'module': 'WORKERS_beta_C69.warm_worker',
                                         'arguments': ['--socket',
                                                       '<private-runtime-socket>'],
                                         'health': {'request': ['kind'],
                                                    'reply': ['ready',
                                                              'pid']},
                                         'ticket_delta_max_paths': 32,
                                         'capture_fields': ['kind',
                                                            'start_by',
                                                            'binding',
                                                            'reuse',
                                                            'paths'],
                                         'accepted_reply': ['accepted',
                                                            'pid when '
                                                            'accepted'],
                                         'completion_reply': ['result'],
                                         'cancel': 'client write-half '
                                                   'close'},
                   'warm_indexed_lifecycle': {'transport': 'newline-delimited '
                                                           'JSON over '
                                                           'private Unix '
                                                           'socket',
                                              'module': 'WORKERS_beta_C69.warm_worker',
                                              'kind': 'indexed_lifecycle',
                                              'fields': ['kind',
                                                         'start_by',
                                                         'request'],
                                              'request': 'task_lifecycle '
                                                         'with '
                                                         'indexed_task or '
                                                         'lifecycle_context',
                                              'accepted_reply': ['accepted',
                                                                 'pid '
                                                                 'when '
                                                                 'accepted'],
                                              'completion_reply': ['result'],
                                              'cancel': 'client '
                                                        'write-half '
                                                        'close'},
                   'task_lifecycle': {'transport': 'cli',
                                      'runner': 'managed_python',
                                      'module': 'WORKERS_beta_C69.lifecycle_worker',
                                      'managed_parent_env': 'ANECHOIC_BETA_WORKER_PARENT_PID',
                                      'input_fields': ['binding',
                                                       'name',
                                                       'arguments',
                                                       'base_generation',
                                                       'structure_sha256'],
                                      'optional_inputs': ['indexed_task',
                                                          'lifecycle_context'],
                                      'operations': ['atom_lifecycle_create_draft',
                                                     'atom_lifecycle_update',
                                                     'atom_lifecycle_promote_draft',
                                                     'atom_lifecycle_change_status',
                                                     'atom_lifecycle_archive',
                                                     'atom_lifecycle_direct_update',
                                                     'atom_lifecycle_create_asset'],
                                      'output': 'native lifecycle outcome '
                                                'and effects on stdout'}},
        'client': {'task_lifecycle': {'component': 'C16',
                                      'interface': 'task_lifecycle'},
                   'manifest_build': {'component_seed': 'CS4',
                                      'transport': 'cli'},
                   'native_snapshot': {'component': 'C30',
                                       'interface': 'native_snapshot'},
                   'realization_graph': {'component': 'C61',
                                         'interface': 'build_graph',
                                         'module': 'WORKERS_beta_C69.realization_graph'}}},
 'state': {'reads': ['pinned Project Manifest and native Atom carriers'],
           'writes': ['staged artifacts for a generation build',
                      'admitted Ticket effects through C16']}}
```

## Component Contract

### Build a transient Beta Atom snapshot

#### Guarantee

Build a pinned Current Atom summary for a standalone snapshot. For a
generation, derive relations using the attested Model. On cold startup,
capture Current and Draft first. Skip archive directories during
foreground traversal. A separate Worker captures their Archived Atoms
after live admission. Seal the snapshot and Graph in the receipt.

Capture against the admitted Model's Status domains. Recheck the capture
when the compiled Model changes those domains.

Use the watcher's completed observation to guard admission of the
startup base for covered inputs. Orchestrator replays observed changes
against that base.

Verify source membership and versions for external or unwatched inputs.
If coverage is lost, verify the affected inputs before admission.
Use a broader capture if their scope is unknown.

For other captures, verify source membership and versions before
admission. With verified watcher coverage, use its completed
observation in place of a second Worker scan.

Derive named Python, JavaScript, and TypeScript Code Units from captured
Modules. Resolve calls to known Functions and Methods using captured
imports and source bindings. Include declaration and call locations. Use
those call sites to check reached effects in Lean.

Reuse captured sources and import sites for bounded antipattern review.
Keep findings with unresolved owners or execution order visible.

Run one admitted Ticket operation per lifecycle invocation. Create a Task
or Epic Draft, revise a Current Task or Epic into a Draft, promote
an exact Draft, change a Current Ticket's status, archive an exact native
Ticket revision, create a Ticket Asset, or update its Markdown body.
Apply the admitted lifecycle definition and
its Ticket tree effects. Require a different Current Atom to declare
the replacement before archive. Refuse Ticket containers. Bind the operation
to the pinned Project. For a single-Atom write, use the admitted SQL
facts, Structure, and Model rules. Read exact pinned sources through
the Adapter. Compile again for coordinated Ticket tree moves and Model input changes.
Capture the affected native carriers against the admitted base and check
their hashes against the write receipt. Return the native outcome and delta,
or an explicit projection error. Do not build a full generation for the write.

For ordinary source changes, revalidate the input signatures of the
accepted Model, Structure, and Graph before and after native capture.
Return the new native snapshot and its base generation when all
inputs match. If only Graph inputs changed and Kernel supplies the
Structure for that base, rebuild the Realization Graph. Return it
with the native snapshot, digests, and updated input proof. Preserve
the accepted Model and Structure. Use a full build if the required
proof is unavailable or changes during capture.

If the Code Analyzer confirms that graph inputs changed during capture,
restart only the analyzer once with the same Model, Structure, and native
capture, and return a build issue if graph inputs change again.

For Incremental Startup, use the compatible persisted checkpoint to
compare the deterministic folder and carrier path inventory and SHA-256
content hashes. Reuse unchanged data. Capture only additions, edits, and
move destinations. Include the previous path of a move and each missing
path as removals in the change set.

Verify Current and Draft changes before live admission. Verify Archive
changes in the background. Require a full reload if the checkpoint
cannot be verified or a Model, Structure, or compiler schema input
changed. When only Realization Graph inputs changed, rebuild the Graph
with the admitted Model and Structure.

For a supported Ticket-only change, capture up to 1,024 named paths
in one fresh Worker. Return their native delta against the accepted base. An
absent file identifies a removal. Use the existing refresh path when
the file scope, Project Manifest, or source cannot be verified.

A managed fresh Worker stops its isolated process group
when its bound Orchestrator exits. Validate the parent binding before
processing the request.

The warm Worker loads its code once. It accepts one Ticket capture
of up to 32 paths before the caller's start deadline. Report the new
child's PID on acceptance. The child runs without a time limit. On
client write-half close, stop and reap its process group. Return no
delta if capture fails or stops. The warm parent can accept another
capture and retains no Project data. Preload the C16 writer in the same
broker. Run a single-Atom write and its exact delta capture in one child.

#### References

AN-S-3334, AN-T-2958, and AN-T-2976.
