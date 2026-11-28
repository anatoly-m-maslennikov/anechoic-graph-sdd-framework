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
  status: "active"
  version: 37
  updated_at: "2026-11-28T15:09:13+00:00"
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
{'code': {'imports': {'only': [
                               'refresh.refresh__shared.digest','header__shared.status_domains', 'project__shared.owned_temporary_root', 'snapshots__shared.NativeSnapshotChanged', 'snapshots__shared.UnrepresentableCarrierDelta', 'sources__shared.mark_startup_timing',
                               'WORKERS_beta_C69__tests.WORKERS_beta_C69__tests__shared.command_with_fixture',
                               'WORKERS_beta_C69__tests.WORKERS_beta_C69__tests__shared.generation_fixture',
                               'analysis.analysis__shared.python_code_units',
                               'analysis.analysis__shared.python_context_restoration',
                               'analysis.analysis__shared.python_import_order',
                               'generation.generation_batches._capture_archive',
                               'generation.graph_consistency._graph_consistency',
                               'generation.managed_request._ArchiveCapture',
                               'generation.managed_request._managed_request',
                               'generation.spec_staging._stage_spec_rows',
                               'generation.generation__shared._BuildFailure',
                               'generation.generation__shared._compile_ingested',
                               'generation.generation__shared._read_compile_receipt',
                               'generation.generation__shared._run_job',
                               'generation.worker_generation._GenerationOptions',
                               'generation.worker_generation._build_generation',
                               'generation.worker_generation._compile_managed_refresh',
                               'generation.worker_graph._build_graph',
                               'generation.worker_graph._graph_only',
                               'generation.worker_graph._rebuild_graph',
                               'refresh.native_refresh._ReuseHint',
                               'refresh.native_refresh._domain_option',
                               'refresh.native_refresh._reuse_hint',
                               'refresh.native_refresh._ticket_delta',
                               'refresh.native_refresh.artifact_inputs',
                               'refresh.native_refresh.deferred_incremental',
                               'refresh.native_refresh.digest',
                               'refresh.native_refresh.refresh',
                               'refresh.native_refresh.reusable_graph',
                               'refresh.native_refresh.startup_incremental',
                               'web_analysis.web_analysis__shared.web_export_aliases',
                               'web_analysis.web_analysis__shared.web_import_review','generation_batches._capture_archive',
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
                               'graph_inputs.graph_input_signature',
                               'manifest_build_CS4__shared.manifest_input_signature',
                               'WORKERS_beta_C69__shared.python_context_restoration',
                               'WORKERS_beta_C69__shared.python_import_order',
                               'WORKERS_beta_C69__shared.python_code_units']},
          'exports': {
                      'refresh.refresh__shared.digest': {'private': ['C69']},
                      'WORKERS_beta_C69__tests.WORKERS_beta_C69__tests__shared.command_with_fixture': {"private": ['LAYER_4_ENGINE_STUDIO_C14/WORKERS_beta_C69/WORKERS_beta_C69__tests/code_analysis', 'LAYER_4_ENGINE_STUDIO_C14/WORKERS_beta_C69/WORKERS_beta_C69__tests/incremental', 'LAYER_4_ENGINE_STUDIO_C14/WORKERS_beta_C69/WORKERS_beta_C69__tests/lifecycle', 'LAYER_4_ENGINE_STUDIO_C14/WORKERS_beta_C69/WORKERS_beta_C69__tests/worker']},
                      'WORKERS_beta_C69__tests.WORKERS_beta_C69__tests__shared.generation_fixture': {"private": ['LAYER_4_ENGINE_STUDIO_C14/WORKERS_beta_C69/WORKERS_beta_C69__tests/generation', 'LAYER_4_ENGINE_STUDIO_C14/WORKERS_beta_C69/WORKERS_beta_C69__tests/incremental', 'LAYER_4_ENGINE_STUDIO_C14/WORKERS_beta_C69/WORKERS_beta_C69__tests/lifecycle', 'LAYER_4_ENGINE_STUDIO_C14/WORKERS_beta_C69/WORKERS_beta_C69__tests/worker']},
                      'analysis.analysis__shared.python_code_units': {'private': ['C69', 'LAYER_4_ENGINE_STUDIO_C14/ARCHITECTURE_ANALYSIS_C73/IMPLEMENTATION_VERIFICATION_C74/carrier', 'LAYER_4_ENGINE_STUDIO_C14/WORKERS_beta_C69/WORKERS_beta_C69__tests/code_analysis']},
                      'analysis.analysis__shared.python_context_restoration': {'private': ['C69', 'LAYER_4_ENGINE_STUDIO_C14/WORKERS_beta_C69/WORKERS_beta_C69__tests/code_analysis']},
                      'analysis.analysis__shared.python_import_order': {'private': ['C69', 'LAYER_4_ENGINE_STUDIO_C14/WORKERS_beta_C69/WORKERS_beta_C69__tests/code_analysis']},
                      'generation.generation_batches._capture_archive': {"private": ['C69', 'LAYER_4_ENGINE_STUDIO_C14/WORKERS_beta_C69/WORKERS_beta_C69__tests/generation']},
                      'generation.graph_consistency._graph_consistency': {"private": ['C69']},
                      'generation.managed_request._ArchiveCapture': {"private": ['LAYER_4_ENGINE_STUDIO_C14/WORKERS_beta_C69/WORKERS_beta_C69__tests/generation']},
                      'generation.managed_request._managed_request': {"private": ['C69']},
                      'generation.spec_staging._stage_spec_rows': {"private": ['C69', 'LAYER_4_ENGINE_STUDIO_C14/WORKERS_beta_C69/WORKERS_beta_C69__tests/generation']},
                      'generation.generation__shared._BuildFailure': {"private": ['C69']},
                      'generation.generation__shared._compile_ingested': {'private': ['C69', 'LAYER_4_ENGINE_STUDIO_C14/WORKERS_beta_C69/WORKERS_beta_C69__tests/generation']},
                      'generation.generation__shared._read_compile_receipt': {"private": ['C69']},
                      'generation.generation__shared._run_job': {"private": ['C69']},
                      'generation.worker_generation._GenerationOptions': {"private": ['C69']},
                      'generation.worker_generation._build_generation': {"private": ['C69']},
                      'generation.worker_generation._compile_managed_refresh': {"private": ['C69']},
                      'generation.worker_graph._build_graph': {"private": ['C69']},
                      'generation.worker_graph._graph_only': {"private": ['C69']},
                      'generation.worker_graph._rebuild_graph': {"private": ['C69']},
                      'refresh.native_refresh._ReuseHint': {"private": ['C69']},
                      'refresh.native_refresh._domain_option': {"private": ['C69']},
                      'refresh.native_refresh._reuse_hint': {"private": ['C69']},
                      'refresh.native_refresh._ticket_delta': {"private": ['C69']},
                      'refresh.native_refresh.artifact_inputs': {"private": ['C69', 'LAYER_4_ENGINE_STUDIO_C14/WORKERS_beta_C69/generation']},
                      'refresh.native_refresh.deferred_incremental': {"private": ['C69']},
                      'refresh.native_refresh.digest': {"private": ['C69', 'LAYER_4_ENGINE_STUDIO_C14/WORKERS_beta_C69/generation']},
                      'refresh.native_refresh.refresh': {"private": ['C69']},
                      'refresh.native_refresh.reusable_graph': {"private": ['C69', 'LAYER_4_ENGINE_STUDIO_C14/WORKERS_beta_C69/generation']},
                      'refresh.native_refresh.startup_incremental': {"private": ['C69']},
                      'web_analysis.web_analysis__shared.web_export_aliases': {"private": ['C69']},
                      'web_analysis.web_analysis__shared.web_import_review': {"private": ['C69']},'generation_batches._capture_archive': {'private': ['LAYER_4_ENGINE_STUDIO_C14/WORKERS_beta_C69/WORKERS_beta_C69__tests',
                          'LAYER_4_ENGINE_STUDIO_C14/WORKERS_beta_C69/WORKERS_beta_C69__tests/generation']},
                      'managed_request._ArchiveCapture': {'private': ['LAYER_4_ENGINE_STUDIO_C14/WORKERS_beta_C69/WORKERS_beta_C69__tests',
                          'LAYER_4_ENGINE_STUDIO_C14/WORKERS_beta_C69/WORKERS_beta_C69__tests/generation']},
                      'WORKERS_beta_C69__shared': {'private': ['LAYER_4_ENGINE_STUDIO_C14/WORKERS_beta_C69/WORKERS_beta_C69__tests',
                          'LAYER_4_ENGINE_STUDIO_C14/WORKERS_beta_C69/WORKERS_beta_C69__tests/generation',
                          'LAYER_4_ENGINE_STUDIO_C14/WORKERS_beta_C69/WORKERS_beta_C69__tests/incremental']},
                      'spec_staging._stage_spec_rows': {'private': ['LAYER_4_ENGINE_STUDIO_C14/WORKERS_beta_C69/WORKERS_beta_C69__tests',
                          'LAYER_4_ENGINE_STUDIO_C14/WORKERS_beta_C69/WORKERS_beta_C69__tests/generation']},
                      'WORKERS_beta_C69__shared._compile_ingested': {'private': ['LAYER_4_ENGINE_STUDIO_C14/WORKERS_beta_C69/WORKERS_beta_C69__tests',
                          'LAYER_4_ENGINE_STUDIO_C14/WORKERS_beta_C69/WORKERS_beta_C69__tests/generation']},
                      'WORKERS_beta_C69__shared.python_context_restoration': {'private': ['LAYER_4_ENGINE_STUDIO_C14/WORKERS_beta_C69/WORKERS_beta_C69__tests',
                          'LAYER_4_ENGINE_STUDIO_C14/WORKERS_beta_C69/WORKERS_beta_C69__tests/code_analysis']},
                      'WORKERS_beta_C69__shared.python_import_order': {'private': ['LAYER_4_ENGINE_STUDIO_C14/WORKERS_beta_C69/WORKERS_beta_C69__tests',
                          'LAYER_4_ENGINE_STUDIO_C14/WORKERS_beta_C69/WORKERS_beta_C69__tests/code_analysis']},
                      'WORKERS_beta_C69__shared.python_code_units': {'private': ['LAYER_4_ENGINE_STUDIO_C14/WORKERS_beta_C69/WORKERS_beta_C69__tests',
                          'LAYER_4_ENGINE_STUDIO_C14/WORKERS_beta_C69/WORKERS_beta_C69__tests/code_analysis',
                                                                                 'LAYER_4_ENGINE_STUDIO_C14/ARCHITECTURE_ANALYSIS_C73/IMPLEMENTATION_VERIFICATION_C74/carrier',
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
generation, derive relations under the attested Model. Capture Current
and Draft first. Skip Archive directories until a separate Worker loads
them after live admission. Seal the snapshot and Graph in the receipt.

Capture under the admitted Status domains and recheck if compilation
changes them. Use the completed watcher observation to guard covered
inputs in place of a second scan. Orchestrator replays changes. Verify
membership and versions for uncovered inputs and coverage gaps. Broaden
capture if their scope is unknown.

Derive named Python, JavaScript, and TypeScript Code Units, declarations,
and call locations from the captured Modules. Resolve calls through
captured imports and bindings. Check reached effects in Lean. Reuse the
same evidence for bounded antipattern review and retain unresolved
ownership and execution order.

Run one admitted Ticket operation in the pinned Project. Support Task or
Epic Draft creation or revision, exact promotion and archive, Current status change,
and asset creation or Markdown update. Enforce the admitted lifecycle,
Ticket tree effects, the different Current replacement required for
archive, and refusal of Ticket containers. For a single-Atom write, use
admitted SQL facts, Structure, and Model rules. Read exact sources through
the Adapter. Compile again for coordinated tree or Model changes.
Validate affected carrier hashes against the write receipt and return
the outcome and native delta or a projection error. Single writes
require no full generation build.

For ordinary source changes, verify the admitted Model, Structure, and
Graph input signatures before and after native capture. Return the native
snapshot against the verified base. With Graph-only changes and the
matching Structure, return a rebuilt Graph with the native snapshot,
digests, and proof. Preserve Model and Structure. Full-build if proof
is unavailable or changes during capture. If Graph inputs change during
analysis, restart the Code Analyzer once with the same Model, Structure,
and capture. A further change yields a build issue.

For Incremental Startup, compare the checkpoint's deterministic folder
and path inventory and SHA-256 content hashes. Capture only additions,
edits, and move destinations. Remove missing and previous paths. Verify
Current and Draft before live admission and Archive in the background.
Require full reload if the checkpoint cannot be verified or Model,
Structure, or compiler schema input changes. Use the admitted Model and
Structure for Graph-only rebuild.

For supported Ticket changes, one fresh Worker captures up to 1,024 named
paths against the base. Absence is removal. Use the broader refresh if
path scope, Manifest, or source proof is unavailable. A fresh Worker
validates its parent and stops its group when the Orchestrator exits.

A warm Worker preloads C16 and accepts one capture of up to 32 paths before
the caller's deadline. Report the child PID. The child runs without a time
limit and stops and is reaped on socket write-half close. Failure or
abort returns no delta. The parent keeps no Project data and can accept
another request. Run a single-Atom write and its delta capture in one child.

#### References

AN-S-3334, AN-T-2958, and AN-T-2976.
